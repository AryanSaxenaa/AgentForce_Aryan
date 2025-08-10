"""Unit tests for TestModifier (Task 6.2)."""
from src.agents import TestModifier
from src.interfaces.base_interfaces import TestSuite, TestCase, TestType, Language


def make_suite():
    return TestSuite(
        language=Language.PYTHON,
        framework='pytest',
        test_cases=[
            TestCase(name='test_add', test_type=TestType.UNIT, function_name='add', description='adds', test_code='def test_add():\n    assert 1+1==2\n'),
            TestCase(name='test_sub', test_type=TestType.UNIT, function_name='sub', description='subs', test_code='def test_sub():\n    x=2-1\n'),
        ],
    )


def test_modify_and_validate():
    suite = make_suite()
    mod = TestModifier()
    # Add assertion to test_sub and rename
    changes = mod.modify_test(suite, 'sub', {'rename': 'test_subtract', 'add_assertion': 'assert x == 1'})
    assert any('renamed' in c for c in changes)
    assert any('added assertion' in c for c in changes)

    # Ensure consistency runs without introducing inconsistencies
    consistency_changes = mod.ensure_consistency(suite)
    assert isinstance(consistency_changes, list)

    # Validate passes
    result = mod.validate(suite)
    assert result.ok, result.issues


def test_add_and_remove():
    suite = make_suite()
    mod = TestModifier()
    # Add
    new = mod.add_test(suite, 'mul')
    assert any(t.name == new.name for t in suite.test_cases)
    # Remove
    removed = mod.remove_test(suite, 'mul')
    assert removed >= 1
