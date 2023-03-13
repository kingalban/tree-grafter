import hypothesis.strategies as st


@st.composite
def _json_keys(draw):
    """ strings and int """
    return draw(st.one_of(st.integers(), st.text()))


@st.composite
def _json_values(draw):
    """ possible values to find in a json """
    return draw(st.one_of(_json_keys(), st.none(), st.booleans()))


@st.composite
def _json_primitives(draw, elements):
    """ json mapping and sequence, aka dict and list """
    return draw(st.one_of(
        st.dictionaries(_json_keys(), elements),
        st.lists(elements)
    ))


@st.composite
def recursive_json(draw, doc_element=st.nothing()):
    """ created json document like list/dict tree structure
        if supplied, 'doc_element' can be inserted as a
    """
    def recurse(children):
        return _json_primitives(st.one_of(children, doc_element))

    return draw(st.recursive(
        _json_primitives(_json_values()),
        recurse
    ))
