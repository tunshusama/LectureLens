from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from test_models_and_renderers import SCRIPTS, PNG_1X1, note, profile
from lecture_notes.models import ModelValidationError, validate_data, validate_profile_match
from lecture_notes import render_lark, render_markdown
from lecture_notes.pathing import file_sha256, build_dir_for_pdf
from run_context import resolve_context


def teaching_profile():
    data = profile()
    data.update(mode='zero_foundation', assumed_knowledge=[])
    return data


def teaching_note():
    data = note('page.png')
    data.update(mode='zero_foundation', reading_guide='先看页面，再做例子。',
                glossary_title='术语总表', self_check={'title': '自测', 'items': [
                    {'question': '怎样比较大小？', 'answer': '1 < 2，所以第一个量更小。', 'pages': [1]}
                ]})
    formula = data['sections'][0]['blocks'][3]
    formula['symbols'][0]['reading'] = 'x'
    formula['symbols'].append({'symbol': 'y', 'reading': 'y', 'meaning': '第二个量'})
    formula['worked_example'] = '代入 x=1，y=2，1 < 2 成立。'
    data['sections'][0]['blocks'].append({
        'type': 'code', 'language': 'python',
        'code': 'if x < y:\n    print("``` & <")',
        'explanation': '先比较两个数，条件成立才执行缩进中的打印。',
    })
    return data


class TeachingContractTests(unittest.TestCase):
    def test_profile_rejects_hidden_prerequisites_and_conflicting_goal(self):
        for update in ({'assumed_knowledge': ['knows statistics']}, {'learning_goal': 'review'}, {'depth': 'concise'}):
            data = teaching_profile()
            data.update(update)
            with self.assertRaises(ModelValidationError):
                validate_data('profile', data)

    def test_detailed_note_and_profile_match(self):
        validate_data('profile', teaching_profile())
        validate_data('note', teaching_note())
        validate_profile_match(teaching_note(), teaching_profile())
        with self.assertRaisesRegex(ModelValidationError, 'mode'):
            validate_profile_match(note('page.png'), teaching_profile())

    def test_missing_teaching_support_is_rejected(self):
        for key in ('worked_example', 'symbols'):
            data = teaching_note()
            if key == 'symbols':
                data['sections'][0]['blocks'][3][key] = []
            else:
                del data['sections'][0]['blocks'][3][key]
            with self.assertRaises(ModelValidationError):
                validate_data('note', data)
        for key in ('self_check', 'glossary_title', 'reading_guide'):
            data = teaching_note()
            del data[key]
            with self.assertRaises(ModelValidationError):
                validate_data('note', data)
        data = teaching_note()
        del data['sections'][0]['blocks'][2]
        with self.assertRaisesRegex(ModelValidationError, 'immediate explanation'):
            validate_data('note', data)

    def test_transition_can_be_brief_but_content_needs_obstacle(self):
        data = teaching_note()
        data['sections'][0]['blocks'] = data['sections'][0]['blocks'][1:3]
        with self.assertRaisesRegex(ModelValidationError, 'learning_note'):
            validate_data('note', data)
        data['sections'][0]['kind'] = 'transition'
        validate_data('note', data)

    def test_review_pages_and_cross_section_coverage(self):
        data = teaching_note()
        data['self_check']['items'][0]['pages'] = [9]
        with self.assertRaisesRegex(ModelValidationError, 'outside this note'):
            validate_data('note', data)
        data = teaching_note()
        data['sections'].append(copy.deepcopy(data['sections'][0]))
        with self.assertRaisesRegex(ModelValidationError, 'across sections'):
            validate_data('note', data)

    def test_cached_profile_does_not_swallow_explicit_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / 'lecture.pdf'
            pdf.write_bytes(b'synthetic source identity')
            build = build_dir_for_pdf(pdf, root)
            build.mkdir(parents=True)
            data = profile()
            data['source_sha256'] = file_sha256(pdf)
            (build / 'profile.json').write_text(json.dumps(data))
            self.assertEqual(resolve_context(pdf, root)['profile_status'], 'reusable')
            self.assertEqual(resolve_context(pdf, root, 'zero_foundation')['profile_status'], 'override_required')
            self.assertEqual(json.loads((build / 'profile.json').read_text()), data)

    def test_both_outputs_preserve_code_examples_and_appendices(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'page.png').write_bytes(PNG_1X1)
            data = teaching_note()
            # Repeating an introduced term must not repeat it in the final glossary.
            data['sections'][0]['blocks'].append(copy.deepcopy(data['sections'][0]['blocks'][4]))
            for renderer, filename in ((render_markdown, 'notes.md'), (render_lark, 'notes.xml')):
                out = renderer.render(data, root / filename, root)
                text = out.read_text()
                self.assertIn('代入 x=1', text)
                self.assertIn('术语总表', text)
                self.assertIn('自测', text)
                self.assertIn('(P1)', text)
                if filename.endswith('xml'):
                    tree = ET.fromstring('<root>' + text + '</root>')
                    self.assertEqual(tree.find('.//pre/code').text, data['sections'][0]['blocks'][-2]['code'])
                else:
                    self.assertIn('````python\nif x < y:\n    print("``` & <")\n````', text)
                self.assertEqual(text.split('术语总表')[1].count('Context'), 1)

    def test_render_cli_requires_profile_and_blocks_mode_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'page.png').write_bytes(PNG_1X1)
            path = root / 'note.json'
            path.write_text(json.dumps(teaching_note()))
            command = [sys.executable, str(SCRIPTS / 'render_notes.py'), str(path),
                       '--out', str(root / 'notes.md'), '--project-root', str(root)]
            missing = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(missing.returncode, 0)
            (root / 'profile.json').write_text(json.dumps(teaching_profile()))
            for fmt in ('markdown', 'lark'):
                result = subprocess.run(command + ['--format', fmt], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = teaching_note()
            del data['mode']
            path.write_text(json.dumps(data))
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('mode must match', result.stdout)


if __name__ == '__main__':
    unittest.main()
