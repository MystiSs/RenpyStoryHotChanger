init python in shcs_store:
    enable_backup = True
    enable_force_reload = False

    #<Избегаю потенциальную проблему с сериализацией (чтобы RenPy не улетал с трейсбеком из-за cPickle)>#
    def get_node_linenumber(node):
        return node.linenumber

    def get_node_lists(node_set):
        node_lists = { }
        for node in node_set:
            if node.filename not in node_lists:
                node_lists[node.filename] = [node]
            else:
                node_lists[node.filename].append(node)

        for node_list in node_lists.values():
            node_list.sort(key=get_node_linenumber)
        
        return node_lists.values()

    def get_tabulation(lines):
        tabulation_from_lines = [ ]
        for line in lines:
            count = 0
            for char in line:
                if char == ' ':
                    count += 1
                else:
                    break
            tabulation_from_lines.append(' ' * count)

        return tabulation_from_lines

    def create_backup(filename, lines):
        physical_path = renpy.loader.get_path(filename).replace("/game", "")
        with open(physical_path + ".bkp", 'w') as file:
            file.write("Бэкап файла {}\n".format(filename.split('/')[-1]))
            file.writelines(lines)

    def rewrite_file_lines(nodes, backup=True):
        physical_path = renpy.loader.get_path(nodes[0].filename).replace("/game", "")
        lines = [ ]
        tabulation = [ ]

        with open(physical_path, 'r') as file:
            lines = file.readlines()
        tabulation = get_tabulation(lines)
        
        for node in nodes:
            if node.linenumber <= 0 or node.linenumber > len(lines):
                renpy.error("Что-то пошло не так...\nОшибка с требуемой строкой в файле\nПроблемный узел: {}".format(node))

        if backup:
            create_backup(node.filename, lines)

        for node in nodes:
            lines[node.linenumber - 1] = tabulation[node.linenumber - 1] + node.ast.get_code() + "\n"

        with open(physical_path, 'w') as file:
            file.writelines(lines)

    def rewrite_files(backup=True):
        node_lists = get_node_lists(changed_dialogue_nodes)
        for node_list in node_lists:
            rewrite_file_lines(node_list, enable_backup)

        if enable_force_reload and not renpy.get_autoreload():
            renpy.reload_script()