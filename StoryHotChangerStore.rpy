init 10 python in shcs_store:
    from renpy.store import shcs_try_update_say_screen as try_update_say_screen
    from renpy.store import shcs_excluded_characters_tags as excluded_characters_tags


    SEARCH_DEPTH = 10
    IF_SEARCH_DEPTH = 10
    MENU_SEARCH_DEPTH = 10

    changed_dialogue_nodes = set()

    def get_say_nodes(from_node):
        #<Шаблон: Кортеж (тип, узел), где тип "RAW", "FROM_IF" или "FROM_MENU">#
        #<Если "FROM_IF, то добавляется ещё два элемента в кортеж: условие, вложенность">#
        #<Если "FROM_MENU, то добавляется ещё три элемента в кортеж: выбор, вложенность, условие (если есть, иначе None)">#
        say_nodes_data = [ ]

        #<Избегание дублирования (на всякий случай)>#
        seen_say_nodes = set()

        next_node = from_node.next
        for i in range(SEARCH_DEPTH):
            if next_node is None:
                return say_nodes_data
            
            if isinstance(next_node, renpy.ast.Say):
                if next_node in seen_say_nodes:
                    continue

                say_nodes_data.append(("RAW", next_node))
                seen_say_nodes.add(next_node)
            
            elif isinstance(next_node, renpy.ast.If):
                if_say_nodes_data = get_say_nodes_from_if_node(next_node, IF_SEARCH_DEPTH)
                for node_data in if_say_nodes_data:
                    if node_data[1] in seen_say_nodes:
                        continue

                    say_nodes_data.append(("FROM_IF", node_data[1], node_data[0], node_data[2]))
                    seen_say_nodes.add(node_data[1])

            elif isinstance(next_node, renpy.ast.Menu):
                menu_say_nodes_data = get_say_nodes_from_menu_node(next_node, MENU_SEARCH_DEPTH)
                for node_data in menu_say_nodes_data:
                    if node_data[1] in seen_say_nodes:
                        continue
                    
                    say_nodes_data.append(("FROM_MENU", node_data[1], node_data[0], node_data[2], node_data[3]))
                    seen_say_nodes.add(node_data[1])
            
            next_node = next_node.next

        return say_nodes_data

    def get_say_nodes_from_translate_node(translate_node):
        return [node for node in translate_node.block if isinstance(node, renpy.ast.Say)]

    def get_say_nodes_from_menu_subblock(node_list, nesting=1):
        """
            Возвращает список Say узлов из условного суб-блока узла Menu (имеется ввиду блок под выбором)
            Вложенность будет сквозной (независимо if блок или menu блок. Вложенность будет общей)
        """

        seen_nodes = set()
        subblock_node_data = [ ]

        for node in node_list:
            if isinstance(node, renpy.ast.Say):
                if node not in seen_nodes:
                    subblock_node_data.append(("RAW", node))
                seen_nodes.add(node)

            elif isinstance(node, renpy.ast.Translate):
                from_translate_nodes = get_say_nodes_from_translate_node(node)
                for node_internal in from_translate_nodes:
                    if node_internal not in seen_nodes:
                        subblock_node_data.append(("RAW", node_internal))
                    seen_nodes.add(node_internal)

            elif isinstance(node, renpy.ast.If):
                from_if_nodes = get_say_nodes_from_if_node(node, IF_SEARCH_DEPTH, nesting + 1)
                for node_data in from_if_nodes:
                    if node_data[1] not in seen_nodes:
                        subblock_node_data.append(("FROM_IF", node_data[1], node_data[0], node_data[2]))
                    seen_nodes.add(node_data[1])

            elif isinstance(node, renpy.ast.Menu):
                from_menu_nodes = get_say_nodes_from_menu_node(node, MENU_SEARCH_DEPTH, nesting + 1)
                for node_data in from_menu_nodes:
                    if node_data[1] not in seen_nodes:
                        subblock_node_data.append(("FROM_MENU", node_data[1], node_data[0], node_data[2], node_data[3]))
                    seen_nodes.add(node_data[1])

        return subblock_node_data

    def _add_say_node_with_condition(say_nodes, condition, node, nesting):
        say_nodes.append((condition, node, nesting))

    def get_say_nodes_from_if_node(if_node, if_depth=10, nesting=1):
        say_nodes = [ ] #<Шаблон: Кортеж (условие, узел, вложенность)>#

        for idx, entry in enumerate(if_node.entries):
            if idx > if_depth:
                break
            
            condition, node_list = entry

            for node in node_list:
                if isinstance(node, renpy.ast.If):
                    nesitng_if_data = get_say_nodes_from_if_node(node, if_depth, nesting + 1)
                    say_nodes.extend(nesitng_if_data)

                elif isinstance(node, renpy.ast.Menu):
                    menu_node_data = get_say_nodes_from_menu_node(node, MENU_SEARCH_DEPTH, nesting + 1)
                    say_nodes.extend(menu_node_data)

                elif isinstance(node, renpy.ast.Translate):
                    say_nodes_from_translate = get_say_nodes_from_translate_node(node)
                    for say_node in say_nodes_from_translate:
                        _add_say_node_with_condition(say_nodes, condition, say_node, nesting)

                elif isinstance(node, renpy.ast.Say):
                    _add_say_node_with_condition(say_nodes, condition, node, nesting)

        #<Блок else помечается как If с условием True>#
        if len(say_nodes) > 1 and say_nodes[-1][0] == "True":
            say_nodes[-1] = ("ELSE", say_nodes[-1][1], say_nodes[-1][2])

        return say_nodes

    def _add_say_node_from_menu(say_nodes, label, node, nesting, condition):
        say_nodes.append((label, node, nesting, condition)) 

    def get_say_nodes_from_menu_node(menu_node, menu_depth=10, nesting=1):
        say_nodes = [ ] #<Шаблон: Кортеж (выбор, узел, вложенность, условие)

        for idx, item in enumerate(menu_node.items):
            if idx > menu_depth:
                break

            label, condition, node_list = item

            #<Суб-блок выбора это по сути вложенность. Следовательно прибавляем тут же 1>#
            subblock_nodes = get_say_nodes_from_menu_subblock(node_list, nesting + 1)
            for subblock_node_data in subblock_nodes:
                #<На данный момент, опускаем всю информацию узлов из If блока, сохраняем лишь сам узел и уровень вложенности>#
                #<Однако информация об условии и вложенности есть и её можно использовать>#
                #<Но если мы столкнулись с узлом из внутреннего меню, то отдаём приоритет ему в плане информации>#
                if subblock_node_data[0] == "FROM_MENU":
                    _add_say_node_from_menu(say_nodes, subblock_node_data[2], subblock_node_data[1], subblock_node_data[3], subblock_node_data[4])
                else:
                    internal_nesting = subblock_node_data[3] if subblock_node_data[0] == "FROM_IF" else nesting
                    _add_say_node_from_menu(say_nodes, label, subblock_node_data[1], internal_nesting, condition)
        
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

    class GameCharacter:
        def __init__(self, tag, name):
            self.tag = tag
            self.name = name

    def get_all_characters():
        result = []
        for tag, char_obj in vars(renpy.store).items():
            if isinstance(char_obj, renpy.character.ADVCharacter):
                result.append(GameCharacter(tag, str(char_obj)))
        return result

    def sort_char_tags(char_data):
        return char_data.name.lower()

    def filter_characters(characters, search, filter_mode):
        if filter_mode == "names":
            chars = [
                char for char in characters
                if search.lower() in char.name.lower()
            ]
        else:
            chars = [
                char for char in characters
                if search.lower() in char.tag.lower()
            ]

        chars = [char for char in chars if char.name not in excluded_characters_tags]
        chars.sort(key=sort_char_tags)

        return chars

    def get_char_name(all_chars, who_tag):
        return next(char.name for char in all_chars if char.tag == who_tag)
