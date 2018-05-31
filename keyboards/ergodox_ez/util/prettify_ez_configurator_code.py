
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


def parse_keymap_line(line):
    """
    Parse a single keymap definition line

    :param line:
    :return:
    """
    # keymap definition line will look like:
    #      " [0] = KEYMAP(KC_EQUAL,KC_1,KC_2,KC_3,KC_4,KC_5, ... RCTL_T(KC_ENTER)), "
    # we wil extract layer name ("0" in this case and key definitions (as a dict)
    line = line.strip()
    line = line.split("=")
    if len(line) != 2:
        raise ValueError("could not parse keymap line: {}".format(line))

    layer_name, layer_keys = line
    layer_name = layer_name.strip()
    layer_keys = layer_keys.strip().upper()

    if not (layer_name.startswith('[') and layer_name.endswith(']')):
        raise ValueError("error parsing layer name: {}".format(layer_name))
    layer_name = layer_name[1:-1]

    if not (layer_keys.startswith("KEYMAP(") and layer_keys.endswith("),")):
        raise ValueError("error parsing layer keys: {}".format(layer_keys))

    print("parsing layer: {}".format(layer_name))
    layer_keys = layer_keys.replace("KEYMAP(", "", 1)
    layer_keys = layer_keys[:-2]

    # layer keys is now a string like:
    #    'KC_EQUAL,KC_1,KC_2,KC_3,KC_4,KC_5,... RCTL_T(KC_ENTER)'
    # we'll convert this to a dict where key is the "KEY_NUMBER" (0 to 80)
    keymap = dict()
    for ikey, key in enumerate(_split_key_definitions(layer_keys)):
      keymap[ikey] = key

    return layer_name, keymap


def _split_key_definitions(line):
    """
    Split a comma seperated line of key definitions (which may have embedded commas)

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

    yield "".join(token)


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
