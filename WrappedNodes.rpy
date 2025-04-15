init 5 python in shcs_store:
    class IWrappedNode:
        """Интерфейс для классов-обёрток AST-узлов диалогов."""

        def replace_in_ast(self):
            raise NotImplementedError("Данный метод должен быть реализован")

        def to_default(self):
            raise NotImplementedError("Данный метод должен быть реализован")

        def to_default_who(self):
            raise NotImplementedError("Данный метод должен быть реализован")

        def to_default_what(self):
            raise NotImplementedError("Данный метод должен быть реализован")

    #############################################################################

    class BaseWrappedNode(IWrappedNode):
        def __init__(self, node):
            self.ast = node

            self.who = node.who
            self.what = node.what

            self.old_who = self.who[:] if self.who else None
            self.old_what = self.what[:]

            self.filename = node.filename
            self.linenumber = node.linenumber

        def replace_in_ast(self):
            pass

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
    
    #############################################################################

    class DialogueNode(BaseWrappedNode):
        def replace_in_ast(self):
            self.ast.who = self.who
            self.ast.what = self.what
