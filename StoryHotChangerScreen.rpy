init:
    style shcs_frame_style:
        background "#000000be"
        padding (5, 5)
        offset (5, 5)

    style shcs_text_style:
        size 14
        color "#ffffff"
        idle_color "#ffffff"
        hover_color "#ffffffab"
        insensitive_color "#ffffff65"
        outlines [(1, "#000000", 0, 0)]

    style shcs_text_other_style is shcs_text_style:
        color "#ffffffa9"

    style shcs_textbutton_style is shcs_text_style:
        background None

    transform shcs_overlay_fadein:
        alpha 0.0
        easein_quad 0.5 alpha 0.05

init 1000:
    $ config.overlay_screens.append("shcs_overlay_controller")

init python:
    import builtins


    shcs_keymap = {
        "show_overlay": ["shift_alt_K_p"],
        "hide_overlay": ["K_ESCAPE", "K_RETURN", "mouseup_3"],

        "hide_input": ["K_ESCAPE"],

        "apply_input": ["K_RETURN", "K_KP_ENTER"],

        "clear_input": ["shift_K_z"],
        "default_input": ["shift_K_a"]
    }

    def shcs_eval_who(who=None):
        """
        Получение объекта персонажа используя его кодовое обозначение. Если None, то это narrator (RenPy делает также).

        Agrs:
            who: Кодовое имя персонажа (название переменной). Возможно, принимает и сам объект, а ast.eval_who() корректно его обработает, но я не уверен.

        Returns:
            ADVCharacter (Character)
        """

        if who is None:
            return narrator
        return renpy.ast.eval_who(who)

    def shcs_try_update_say_screen(node, screen=None):
        """
        Обновляет экран диалогов (экран отображения диалога) с использованием данных из узла диалога.

        Args:
            node: Узел диалога (обычно объект класса ast.Say).
            screen: Имя экрана диалогов для обновления. Если не указано, используется значение из объекта персонажа.

        Returns:
            None
        """

        if node != shcs_get_node(renpy.game.context().current):
            return

        who_instance = shcs_eval_who(node.who)
        screen_name = screen or who_instance.screen
        if renpy.get_screen(screen_name) is None:
            return

        if node.what is not None:
            what_widget = renpy.get_displayable(screen_name, "what")
            if what_widget:
                what = node.what
                what_widget.set_text(what)
        if who_instance is not None:
            who_widget = renpy.get_displayable(screen_name, "who")
            if who_widget:
                who_widget.set_text(who_instance)

    @renpy.pure
    def shcs_dialogue_shorter(text, max_length=64):
        if builtins.len(text) > max_length:
            return text[:max_length] + "..."
        return text

    def shcs_get_node(node_name):
        return renpy.game.script.lookup(node_name)

    def shcs_try_get_next_node_by_depth(node, depth=1):
        current_node = node
        for i in range(depth):
            if current_node is None:
                return None

            current_node = current_node.next
        
        return current_node

screen shcs_line_as_code(node):
    zorder 1100

    $ code_line = node.get_code()

    frame:
        style "shcs_frame_style"
        align (1.0, 0.0)

        text "Код: [code_line]" style "shcs_text_style"

screen shcs_overlay_controller():
    zorder 1000

    if renpy.get_screen("shcs_overlay") is None:
        key shcs_keymap["show_overlay"] action Show("shcs_overlay")

screen shcs_overlay():
    zorder 1000
    tag shcs_overlay
    modal True

    default context = renpy.game.context()
    default next_nodes_depth = 10

    key shcs_keymap["hide_overlay"] action Hide("shcs_overlay")

    add "black" at shcs_overlay_fadein

    frame:
        style "shcs_frame_style"
        align (1.0, 0.0)
        ypos 0.2
        xoffset -5

        has vbox

        hbox:
            textbutton "Резервная копия: ":
                style "shcs_textbutton_style"
                text_style "shcs_text_style"
            
                action ToggleField(shcs_store, "enable_backup")

            text "{}".format("{color=#3cbd00}Да{/color}" if shcs_store.enable_backup else "{color=#af0000}Нет{/color}") style "shcs_text_style"

        hbox:
            textbutton "Перезагрузка скрипта: ":
                style "shcs_textbutton_style"
                text_style "shcs_text_style"
            
                action ToggleField(shcs_store, "enable_force_reload")

            text "{}".format("{color=#3cbd00}Да{/color}" if shcs_store.enable_force_reload else "{color=#af0000}Нет{/color}") style "shcs_text_style"
        
        if renpy.get_autoreload() and not shcs_store.enable_force_reload:
            text "Скрипт будет перезагружен при сохранении изменений. У вас включена перезагрузка скрипта от RenPy (Shift + R, чтобы отключить).":
                style "shcs_text_other_style"
                xmaximum 240

        add Null(0, 12)

        textbutton "Сохранить изменения":
            style "shcs_textbutton_style"
            text_style "shcs_text_style"

            sensitive shcs_store.changed_dialogue_nodes
            action Function(shcs_store.rewrite_files)

    frame:
        style "shcs_frame_style"

        has vbox
        text "Текущий узел: [context.current]" style "shcs_text_style"

    vbox:
        yoffset 48
        spacing 12

        frame:
            style "shcs_frame_style"

            has vbox:
                first_spacing 10
            
            $ current_node_instance = shcs_get_node(context.current)
            if not isinstance(current_node_instance, renpy.ast.Say):
                text "Текущий узел не реплика" style "shcs_text_style"
                text "Тип текущего узла: {}".format(builtins.type(shcs_get_node(current_node_instance))) style "shcs_text_style"
            else:
                vbox:
                    textbutton ">> Текущий узел с репликой: {}".format(shcs_dialogue_shorter(current_node_instance.what)):
                        style "shcs_textbutton_style"
                        text_style "shcs_text_style"

                        hovered Show("shcs_line_as_code", node=current_node_instance)
                        unhovered Hide("shcs_line_as_code")
                        action [Show("shcs_change_text", node=current_node_instance), Hide("shcs_line_as_code")]
                        # alternate [Show("shcs_change_text", node=current_node_instance, mode="who"), Hide("shcs_line_as_code")]

                    text "Файл: {} | Строка: [current_node_instance.linenumber]".format(current_node_instance.filename.split('/')[-1]):
                        style "shcs_text_other_style"

            add Null(0, 24)
            text "Следующие <Say> узлы | Глубина поиска: [next_nodes_depth]" style "shcs_text_style"
            add Null(0, 24)

            if context.current:
                for idx in range(next_nodes_depth):
                    $ next_node = shcs_try_get_next_node_by_depth(current_node_instance, idx + 1)

                    if next_node is None:
                        pass

                    elif isinstance(next_node, renpy.ast.Say):
                        vbox:
                            textbutton ">> Узел с репликой {}: {} {}".format(idx + 1, next_node.who, shcs_dialogue_shorter(next_node.what)):
                                style "shcs_textbutton_style"
                                text_style "shcs_text_style"

                                hovered Show("shcs_line_as_code", node=next_node)
                                unhovered Hide("shcs_line_as_code")
                                action [Show("shcs_change_text", node=next_node), Hide("shcs_line_as_code")]
                                # alternate [Show("shcs_change_text", node=next_node, mode="who"), Hide("shcs_line_as_code")]

                            text "Файл: {} | Строка: [next_node.linenumber]".format(next_node.filename.split('/')[-1]):
                                style "shcs_text_other_style"
        
        frame:
            style "shcs_frame_style"

            has vbox

            if not shcs_store.changed_dialogue_nodes:
                text "Вы ещё ничего не изменили" style "shcs_text_other_style"
            
            else:
                text "Измененные узлы:" style "shcs_text_other_style"

            for node in shcs_store.changed_dialogue_nodes:
                vbox:
                    hbox:
                        text ">> Изменённый узел: " style "shcs_text_style"
                        textbutton "[node.ast.who] ":
                            style "shcs_textbutton_style"
                            text_style "shcs_text_style"

                            hovered Show("shcs_line_as_code", node=node.ast)
                            unhovered Hide("shcs_line_as_code")
                            action [Show("shcs_change_sayer", node=node.ast), Hide("shcs_line_as_code")]

                        textbutton shcs_dialogue_shorter(node.ast.what):
                            style "shcs_textbutton_style"
                            text_style "shcs_text_style"

                            hovered Show("shcs_line_as_code", node=node.ast)
                            unhovered Hide("shcs_line_as_code")
                            action [Show("shcs_change_text", node=node.ast, mode="what"), Hide("shcs_line_as_code")]

                    hbox:
                        textbutton "Сбросить персонажа":
                            style "shcs_textbutton_style"
                            text_style "shcs_text_style"
        
                            action Function(node.to_default_who)

                        text "|" style "shcs_text_style"

                        textbutton "Сбросить реплику":
                            style "shcs_textbutton_style"
                            text_style "shcs_text_style"

                            action Function(node.to_default_what)

                        text "|" style "shcs_text_style"

                        textbutton "Сбросить и убрать":
                            style "shcs_textbutton_style"
                            text_style "shcs_text_style"

                            action Function(shcs_store.try_remove_changed, node)

                    text "Файл: {} | Строка: [node.linenumber]".format(node.filename.split('/')[-1]):
                        style "shcs_text_other_style"

screen shcs_change_text(node, mode="what"):
    zorder 1100
    modal True

    default tools = shcs_store
    default initial_state = node.what if mode == "what" else node.who
    default safe_string = tools.make_tags_safe(initial_state)

    key config.keymap["skip"] action NullAction()

    key shcs_keymap["hide_input"] action Hide("shcs_change_text")
    key shcs_keymap["clear_input"] action SetScreenVariable("safe_string", "")
    key shcs_keymap["default_input"] action SetScreenVariable("safe_string", tools.make_tags_safe(initial_state))

    frame:
        style "shcs_frame_style"
        xmaximum 960
        align (0.5, 0.5)

        has vbox

        $ tags_check_result = tools.is_tags_correct(safe_string, True)
        if not tags_check_result[0]:
            text "Неправильные теги: {}".format(tools.make_tags_safe(tags_check_result[1])) style "shcs_text_style" color "#af0000"
        else:
            text "Ошибок не выявлено." style "shcs_text_style" color "#3cbd00"

            key shcs_keymap["apply_input"] action [Function(tools.try_add_changed, node, safe_string, mode), Hide("shcs_change_text")]

        add Null(0, 24)

        input:
            value ScreenVariableInputValue("safe_string")
            style "shcs_text_style"
            copypaste True    

screen shcs_change_sayer(node, search=""):
    zorder 1100
    modal True

    default tools = shcs_store
    default typed_search = search
    default page = 0

    default all_chars = tools.get_all_characters()
    default current_who_tag = node.who if node.who else "narrator"
    default current_who_name = all_chars[current_who_tag]
    
    default filtered_chars = tools.filter_characters(all_chars, search)

    #TODO: Возможно, стоит вынести режим фильтрации вне экрана, чтобы состояние сохранялось#
    default filter_mode = "tags"
    $ current_filter_mode = "{color=#3cbd00}Тег{/color}" if filter_mode == "tags" else "{color=#3cbd00}Имя{/color}"

    $ chars_per_page = 10
    $ chars_total = len(filtered_chars)
    $ total_pages = (chars_total + chars_per_page - 1) // chars_per_page

    $ start_idx = page * chars_per_page
    $ end_idx = start_idx + chars_per_page
    $ page_chars = filtered_chars[start_idx:end_idx]

    key shcs_keymap["hide_input"] action Hide("shcs_change_sayer")
    key shcs_keymap["apply_input"] action [Show("shcs_change_sayer", node=node, search=typed_search)]

    frame:
        style "shcs_frame_style"
        xmaximum 960
        align (0.5, 0.5)

        has vbox

        text "Тэг говорящего: [current_who_tag]" style "shcs_text_other_style"
        text "Имя говорящего: [current_who_name]" style "shcs_text_other_style"
        
        text "Режим фильтрации: [current_filter_mode]" style "shcs_text_other_style"
        text "Чтобы найти нужного персонажа, введите часть {}:".format("его тега (переменной)" if filter_mode == "tags" else "его имени"):
            style "shcs_text_other_style"

        add Null(0, 10)

        input:
            value ScreenVariableInputValue("typed_search")
            style "shcs_text_style"

        add Null(0, 10)

        if not page_chars:
            text "Нет совпадений" style "shcs_text_style"
        else:
            for char_tag, char_name in page_chars:
                textbutton char_name + " — " + char_tag:
                    style "shcs_textbutton_style"
                    text_style "shcs_text_style"
                    action [
                        Function(tools.try_add_changed, node, char_tag, "who"),
                        Hide("shcs_change_sayer")
                    ]

            add Null(0, 10)
            hbox:
                spacing 20
                if page > 0:
                    textbutton "<< Пред. страница":
                        style "shcs_textbutton_style"
                        text_style "shcs_text_style"
                        action SetScreenVariable("page", page - 1)

                if page < total_pages - 1:
                    textbutton "След. страница >>":
                        style "shcs_textbutton_style"
                        text_style "shcs_text_style"
                        action SetScreenVariable("page", page + 1)

                text "Страница {}/[total_pages]".format(page + 1) style "shcs_text_style"