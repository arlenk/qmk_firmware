
LAYOUT_FORMATS = {

    "EXTRA_WIDE":
    """

.--------------------------------------------------------------. .--------------------------------------------------------------.
| KEY_00 | KEY_01 | KEY_02 | KEY_03 | KEY_04 | KEY_05 | KEY_06 | | KEY_38 | KEY_39 | KEY_40 | KEY_41 | KEY_42 | KEY_43 | KEY_44 |
!--------+--------+--------+--------+--------+-----------------! !--------+--------+--------+--------+--------+-----------------!
| KEY_07 | KEY_08 | KEY_09 | KEY_10 | KEY_11 | KEY_12 | KEY_13 | ! KEY_45 | KEY_46 | KEY_47 | KEY_48 | KEY_49 | KEY_50 | KEY_51 |
!--------+--------+--------+--------x--------x--------!        ! !        !--------x--------x--------+--------+--------+--------!
| KEY_14 | KEY_15 | KEY_16 | KEY_17 | KEY_18 | KEY_19 |--------! !--------! KEY_52 | KEY_53 | KEY_54 | KEY_55 | KEY_56 | KEY_57 |
!--------+--------+--------+--------x--------x--------! KEY_26 ! ! KEY_58 !--------x--------x--------+--------+--------+--------!
| KEY_20 | KEY_21 | KEY_22 | KEY_23 | KEY_24 | KEY_25 |        | !        | KEY_59 | KEY_60 | KEY_61 | KEY_62 | KEY_63 | KEY_64 |
'--------+--------+--------+--------+--------+-----------------' '-----------------+--------+--------+--------+--------+--------'
 | KEY_27| KEY_28 | KEY_29 | KEY_30 | KEY_31 |                                     ! KEY_65 | KEY_66 | KEY_67 | KEY_68 | KEY_69|
 '-------------------------------------------'                                     '-------------------------------------------'
                                             .-----------------. .-----------------.
                                             | KEY_32 | KEY_33 | ! KEY_70 | KEY_71 |
                                    .--------+--------+--------! !--------+--------+--------.
                                    !        !        | KEY_34 | ! KEY_72 |        !        !
                                    ! KEY_35 ! KEY_36 !--------! !--------! KEY_74 ! KEY_75 !
                                    |        |        | KEY_37 | ! KEY_73 |        |        |
                                    '--------------------------' '--------------------------'
    """,
}


def get_layout_definitions(lines):
    """
    Extra and parse layer definitions from source lines

    :param lines: List[str]
    :return: dict[str->dict]

    """
    layer_definition_lines = _extract_layer_definitions(lines)
    layer_definition_lines = _group_layer_definitions(layer_definition_lines)

    layers = dict()
    for line in layer_definition_lines:
        layer_name, layer_definition = _parse_layer_line(line)
        layers[layer_name] = layer_definition

    return layers


def _group_layer_definitions(lines):
    """
    Group (potentially) multi line layer definitions into one line per defition

    :param lines: List[str]
        lines of layer definition source code (from extract_layer_definitions)

    :return: List[str]
        one line per layer

    """
    layers = []

    # each layer is defined with a line (or multiple lines) like
    #   '[MDIA] = LAYOUT_ergodox(',
    #      ...
    #    'KC_TRNS, KC_TRNS, KC_WBAK',
    #    '),'
    #
    # we'll split based on layer names (ie, the [MDIA] above)
    # since layer definitions have commas in them, we can't use ending comma
    # to find eny of each layer so we'll just keep going till the next
    # layer name (or till we reach the end of lines)
    definition = []
    for iline, line in enumerate(lines):
        line = line.strip()
        if line.startswith("["):
            # found start of a layer definition.. if we were already
            # in an existing layer definition, append to knwon layers
            # and start over
            if len(definition):
                layers.append(definition)
                definition = []

        definition.append(line)

    # make sure to catch last layer definition
    if len(definition):
        layers.append(definition)

    layers = ["".join(definition) for definition in layers]

    return layers


def _extract_layer_definitions(lines):
    """
    Find all layout definitions in lines of source code

    :param lines: List[str]
        lines of source code
    :return: List[str]
        lines that contain layer definitions

    """
    LAYERS_DEFINITIONS_START = "const uint16_t PROGMEM keymaps"

    # first, find start of layer definitions.  These are defined in lines like:
    #
    # const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    #
    #   [0] = KEYMAP(KC_EQUAL,KC_1,KC_2,KC_3, ...
    #
    #   [1] = KEYMAP(KC_ESCAPE,KC_F1,KC_F2, ...
    #   ...
    # };
    for iline, line in enumerate(lines):
        line = line.strip()
        if line.startswith(LAYERS_DEFINITIONS_START):
            # for now.. assume start of definitions (and end of definitions)
            # are on their own lines.  No reason this has to be true, but it's much
            # easier to parse if we assume it's true and all files in qmk layouts
            # are formatted like this
            if not line.endswith("{"):
                raise ValueError("can only handle layer definitions that are on separate lines")
            break
    else:
        raise ValueError("could not find start of layer definitions.  "
                         "Looking for: {}".format(LAYERS_DEFINITIONS_START))

    lines = lines[(iline+1):]

    # now keep reading till we get to closing "};"
    layer_definitions = []

    in_multi_line_comment = False
    for iline, line in enumerate(lines):
        line = line.strip()

        # ignore multi-line comments
        if line.startswith("/*"):
            in_multi_line_comment = True

        if in_multi_line_comment:
            if line.endswith("*/"):
                in_multi_line_comment = False
            continue

        # ignore single line comments
        if "//" in line:
            line = line.split('//')[0].strip()

        # we shouldn't find any more open brackets (start of declaration)
        # so throw error if we do
        if "{" in line:
            raise ValueError("error parsing line, not expecting nested declaration: {}".format(line))

        # are we at end of declaration?
        if "};" in line:
            if len(line) > 2:
                raise ValueError("expecting declaration end to be its own line: {}".format(line))
            break

        # if not.. this line must be part of declaration
        if len(line) > 0:
            layer_definitions.append(line)

    return layer_definitions


def _parse_layer_line(line):
    """
    Parse a single layer definition line

    :param line: str
    :return: str, dict
        layer name and dict of key values

    """
    LAYER_DEFINITION_START = ('KEYMAP(', 'LAYOUT(', 'LAYOUT_ergodox(')

    # layer definition line will look like:
    #      " [0] = KEYMAP(KC_EQUAL,KC_1,KC_2,KC_3,KC_4,KC_5, ... RCTL_T(KC_ENTER)), "
    # KEYMAP can also be LAYOUT or LAYOUT_ergodox
    #
    # we wil extract layer name ("0" in this case and key definitions (as a dict)
    line = line.strip()
    line = line.split("=")
    if len(line) != 2:
        raise ValueError("could not parse layer line: {}".format(line))

    layer_name, layer_keys = line
    layer_name = layer_name.strip()
    layer_keys = layer_keys.strip()

    if not (layer_name.startswith('[') and layer_name.endswith(']')):
        raise ValueError("error parsing layer name: {}".format(layer_name))
    layer_name = layer_name[1:-1]

    if not (layer_keys.startswith(LAYER_DEFINITION_START) and layer_keys.endswith("),")):
        raise ValueError("error parsing layer keys: {}".format(layer_keys))

    print("parsing layer: {}".format(layer_name))
    for token in LAYER_DEFINITION_START:
        if token in layer_keys:
            layer_keys = layer_keys.replace(token, "", 1)
            break
    layer_keys = layer_keys[:-2]

    # layer keys is now a string like:
    #    'KC_EQUAL,KC_1,KC_2,KC_3,KC_4,KC_5,... RCTL_T(KC_ENTER)'
    # we'll convert this to a dict where key is the "KEY_NUMBER" (0 to 80)
    layer_definition = dict()
    for ikey, key in enumerate(_split_key_definitions(layer_keys)):
        layer_definition[ikey] = key.strip()

    return layer_name, layer_definition


def _split_key_definitions(line):
    """
    Split a comma separated line of key definitions (which may have embedded commas)

    :param line: str
    :return: generator of strs

    """

    open_parens = 0

    token = []
    for ichar, char in enumerate(line):
        # print("ichar[{}] = {} (open parens={})".format(ichar, char, open_parens))
        if char == ",":
            if open_parens == 0:
                token = "".join(token)
                # print("yielding token {}, remaining is: {}".format(token, line[ichar:]))
                yield token
                token = []
                continue

        elif char == "(":
            open_parens += 1

        elif char == ")":
            open_parens -= 1

        token.append(char)

    token = "".join(token)
    yield token.strip()


def fill_format(fmt, keymap):
    """
    Replace placeholders in format string with appropriate key names

    :param fmt: str
    :param keymap: dict
    :return: str

    """

    for key_number, key_value in keymap.items():
        place_holder = "KEY_{:02.0f}".format(key_number)
        value = key_value.replace("KC_", "").center(len(place_holder))
        value = value[:len(place_holder)]

        fmt = fmt.replace(place_holder, value)

    return fmt
