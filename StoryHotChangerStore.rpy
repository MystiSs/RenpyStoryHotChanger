init python in shcs_store:
    from renpy.store import shcs_try_update_say_screen as try_update_say_screen


    changed_dialogue_nodes = set()

    class DialogueNode:
        def __init__(self, node):
            self.ast = node

            self.who = node.who
            self.what = node.what

            self.old_who = self.who[:] if self.who else None
            self.old_what = self.what[:]

            self.filename = node.filename
            self.linenumber = node.linenumber

        def replace_in_ast(self):
            self.ast.who = self.who
            self.ast.what = self.what

        def to_default(self):
            self.who = self.old_who
            self.what = self.old_what
            self.replace_in_ast()

        def to_default_who(self):
            self.who = self.old_who
            self.replace_in_ast()

        def to_default_what(self):
            self.what = self.old_what
            self.replace_in_ast()

        def __eq__(self, other):
            return self.filename == other.filename and self.linenumber == other.linenumber and self.who == other.who

    def make_tags_safe(text):
        return text.replace('{', '<').replace('}', '>')

    def make_true_tags(text):
        return text.replace('<', '{').replace('>', '}')

    def is_tags_correct(text, need_to_convert=False):
        if need_to_convert:
            text = make_true_tags(text)

        error_string = renpy.check_text_tags(text)
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

        set_text_by_mode(dialogue_node, make_true_tags(new_text), mode)

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
            # TODO: стоит проверить, какое будет поведение с другими типами персонажей
            if isinstance(char_obj, renpy.character.ADVCharacter):
                result[tag] = str(char_obj)
        return result

    def filter_characters(characters, search):
        chars = []
        for char_tag, char_name in characters.items():
            if search.lower() in char_tag.lower():
                chars.append((char_tag, char_name))
        chars.sort(key=lambda x: x[1].lower())
        return chars
