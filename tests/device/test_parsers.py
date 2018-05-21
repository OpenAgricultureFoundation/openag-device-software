import pytest
from device.parsers import RecipeParser

#------------------------------------------------------------------------------
def test_recipe_parser_no_recipe():
    # should except for no recipe
    with pytest.raises( KeyError ):
        recipe_dict = {}
        recipe_parser = RecipeParser()
        transitions = recipe_parser.parse( recipe_dict )

#------------------------------------------------------------------------------
def test_recipe_parser_minimum_recipe():
    # test a minimum recipe
    minimum_dict = {}
    minimum_dict['environments'] = {'env1': {'name':'1'}}
    minimum_dict['phases'] = [{'name':'2', 'repeat':3, 'cycles':[] }]
    cycle_hours = {'name':'4', 'environment':'env1', 'duration_hours':5}
    cycle_mins = {'name':'4', 'environment':'env1', 'duration_minutes':6}
    minimum_dict['phases'][0]['cycles'].append( cycle_hours )
    recipe_parser = RecipeParser()
    transitions = recipe_parser.parse( minimum_dict )
    hours_transitions = [{'minute': 0, 'phase': '2', 'cycle': '4', 'environment_name': '1', 'environment_state': {}}, {'minute': 300, 'phase': '2', 'cycle': '4', 'environment_name': '1', 'environment_state': {}}, {'minute': 600, 'phase': '2', 'cycle': '4', 'environment_name': '1', 'environment_state': {}}, {'minute': 900, 'phase': 'End', 'cycle': 'End', 'environment_name': 'End', 'environment_state': {}}]
    assert transitions == hours_transitions, "Transitions do not match"
            
    # test an alternative cycle duration
    minimum_dict['phases'][0]['cycles'][0] = cycle_mins # replace hours
    transitions = recipe_parser.parse( minimum_dict )
    mins_transitions = [{'minute': 0, 'phase': '2', 'cycle': '4', 'environment_name': '1', 'environment_state': {}}, {'minute': 6, 'phase': '2', 'cycle': '4', 'environment_name': '1', 'environment_state': {}}, {'minute': 12, 'phase': '2', 'cycle': '4', 'environment_name': '1', 'environment_state': {}}, {'minute': 18, 'phase': 'End', 'cycle': 'End', 'environment_name': 'End', 'environment_state': {}}]
    assert transitions == mins_transitions, "Transitions do not match"

