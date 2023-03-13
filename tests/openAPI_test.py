from tree_grafter import openAPI


def test_ref_replacement():
	doc = {
		"prop1": {"$ref": "#/prop2"},
		"prop2": {"a":"a", "b": "b"}
		}

	replaced_doc = openAPI.parse_openAPI_doc(doc)

	assert replaced_doc != doc, "looks like we didn't make any changes?!"
	assert replaced_doc["prop1"] == replaced_doc["prop2"] 


def test_ref_and_allOf():
	doc = {
		"final_properties": {
			"allOf": [
				{"$ref": "#/prop1"}, 
				{"$ref": "#/prop2"}
			]
		},
		"prop1": {"$ref": "#/prop2"},
		"prop2": {"a": "a", "b": "b"}
		}

	replaced_doc = openAPI.parse_openAPI_doc(doc)

	assert replaced_doc != doc, "looks like we didn't make any changes?!"
	assert replaced_doc["prop1"] == replaced_doc["prop2"] 
