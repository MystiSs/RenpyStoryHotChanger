init 10 python in shcs_store:
    from renpy.store import shcs_try_update_say_screen as try_update_say_screen
    from renpy.store import shcs_excluded_characters_tags as excluded_characters_tags


    changed_dialogue_nodes = set()

    def get_nodes(from_node, depth=15):
        nodes = []
        next_node = from_node.next

        for i in range(depth):
            if next_node is None:
                return nodes

            nodes.append(next_node)
            next_node = next_node.next
        
        return nodes

    def get_say_nodes(from_node, depth=10, if_depth=10):
        #<Шаблон: Кортеж (тип, узел), где тип "RAW" или "FROM_IF" (на данный момент)>#
        #<Если "FRON_IF, то добавляется ещё один элемент в кортеж: условие">#
        say_nodes_data = [ ]

        #<Избегание дублирования (на всякий случай)>#
        seen_say_nodes = set()

        next_node = from_node.next
        for i in range(depth):
            if next_node is None:
                return say_nodes_data
            
            if isinstance(next_node, renpy.ast.Say):
                if next_node in seen_say_nodes:
                    continue

                say_nodes_data.append(("RAW", next_node))
                seen_say_nodes.add(next_node)
            
            elif isinstance(next_node, renpy.ast.If):
                if_say_nodes_data = get_say_nodes_from_if_node(next_node)
                for node_data in if_say_nodes_data:
                    if node_data[1] in seen_say_nodes:
                        continue

                    say_nodes_data.append(("FROM_IF", node_data[1], node_data[0]))
                    seen_say_nodes.add(node_data[1])
            
            next_node = next_node.next

        return say_nodes_data

    def get_say_nodes_from_translate_node(translate_node):
        return [node for node in translate_node.block if isinstance(node, renpy.ast.Say)]

    def _add_say_node_with_condition(say_nodes, condition, node):
        say_nodes.append((condition, node))

    def get_say_nodes_from_if_node(if_node, if_depth=10):
        say_nodes = [ ] #<Шаблон: Кортеж (условие, узел)>#

        for idx, entry in enumerate(if_node.entries):
            if idx > if_depth:
                break
            
            condition, node_list = entry

            for node in node_list:
                if isinstance(node, renpy.ast.Translate):
                    say_nodes_from_translate = get_say_nodes_from_translate_node(node)
                    for say_node in say_nodes_from_translate:
                        _add_say_node_with_condition(say_nodes, condition, say_node)

                elif isinstance(node, renpy.ast.Say):
                    _add_say_node_with_condition(say_nodes, condition, node)

        #<Блок else помечается как If с условием True>#
        if say_nodes[-1][0] == "True":
            say_nodes[-1] = ("ELSE", say_nodes[-1][1])

        return say_nodes

    def make_tags_safe(text):
        return text.replace('{', '<').replace('}', '>')

    def make_true_tags(text):
        return text.replace('<', '{').replace('>', '}')

    def is_tags_correct(text, need_to_convert=False):
        if need_to_convert:
            text = make_true_tags(text)

        error_string = renpy.check_text_tags(text)
        if error_string:
            error_string = error_string.decode("unicode-escape")

        return (error_string is None, error_string)

    def set_text_by_mode(node, new_text, mode):
        if mode == "what":
            node.what = new_text
        elif mode == "who":
            node.who = new_text
        
        node.replace_in_ast()
        try_update_say_screen(node.ast)

    def is_text_equal(node, new_text, mode):
        if mode == "what":
            return node.what == new_text
        elif mode == "who":
            return node.who == new_text

    def find_by_node(node):
        for dialogue_node in changed_dialogue_nodes:
            if dialogue_node.ast == node:
                return dialogue_node
        return None

    def try_add_changed(node, new_text, mode="what"):
        old_node = find_by_node(node)
        if old_node is not None:
            if is_text_equal(old_node, new_text, mode):
                return

            set_text_by_mode(old_node, new_text, mode)
            return

        dialogue_node = DialogueNode(node)

        if is_text_equal(dialogue_node, new_text, mode):
            return

        if mode == "what":
            new_text = make_true_tags(new_text)
        set_text_by_mode(dialogue_node, new_text, mode)

        changed_dialogue_nodes.add(dialogue_node)

    def try_remove_changed(node):
        dialogue_node = find_by_node(node)
        if dialogue_node is None:
            return
        
        dialogue_node.to_default()
        changed_dialogue_nodes.discard(dialogue_node)
        try_update_say_screen(node.ast)

    def to_default(node):
        dialogue_node = find_by_node(node)
        if dialogue_node is None:
            return

        dialogue_node.to_default()
        try_update_say_screen(node.ast)

    def get_all_characters():
        result = {}
        for tag, char_obj in vars(renpy.store).items():
            if isinstance(char_obj, renpy.character.ADVCharacter):
                result[tag] = str(char_obj)
        return result

    def sort_char_tags(char_data):
        return char_data[1].lower()

    def filter_characters(characters, search):
        chars = []
        for char_tag, char_name in characters.items():
            if search.lower() in char_tag.lower():
                chars.append((char_tag, char_name))

        chars = [char for char in chars if char[1] not in excluded_characters_tags]

        chars.sort(key=sort_char_tags)
        return chars
