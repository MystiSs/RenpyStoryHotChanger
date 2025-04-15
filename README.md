# 💬 RenpyStoryHotChanger
> 🈯 Интерактивный инструмент для горячего редактирования реплик в Ren'Py  
> 🌍 Interactive dialogue editor tool for Ren'Py games

---

## 🇷🇺 Русская версия

### 📌 Описание

**RenpyStoryHotChanger** — это расширение для визуальных новелл на Ren'Py, позволяющее находить и изменять `Say`-узлы (ast.Say, а если проще – реплики персонажей из `.rpy` файлов) прямо во время выполнения игры. С его помощью можно быстро редактировать диалоги, не покидая игру, что делает процесс написания и отладки сценариев удобнее (возможно).

---

### 🚀 Возможности

✅ Поиск AST `Say`-узлов практически всех видов:
- Базовые (`RAW`) – реплики, которые находятся в `label`-ах на 1-й табуляции (4 пробела)
- Внутри `if`-блоков (`FROM_IF`)
- Внутри `menu`-блоков (`FROM_MENU`)
- Второй и третий вид поддерживает рекурсивный поиск. Например:

  ```renpy
  menu:
      "Как поступить?":
          "Пойти налево":
              if is_night:
                  "Темно как в подземелье."
              else:
                  "На улице солнечно."
  ```
Будут найдены все фразы: "Темно как в подземелье.", "На улице солнечно."

✅ Поддержка условий и вложенности:

- Сохраняется информация об условиях и глубине узла

✅ Визуальный интерфейс:

- Встроенный экран редактирования с удобным UI

✅ Горячее редактирование:

- Изменения применяются сразу и могут быть сохранены в .rpy файл

✅ Безопасность:

- Создание резервных копий оригинального текста
- Проверка корректности тэгов и форматирования

-----------------------------------------------
## 🇬🇧 English Version

### 📌 Description

**RenpyStoryHotChanger** is a Ren'Py extension that allows you to find and edit dialogue (ast.Say) nodes live — directly during gameplay. Perfect for writers who want to polish their story without constantly jumping back to code.

### 🚀 Features

✅ Finds all types of dialogue (Say) nodes:

- Basic (RAW) – lines at the root level of a label block

- Inside if blocks (FROM_IF)

- Inside menu choices (FROM_MENU)

- Both if and menu blocks are recursively searched, e.g.:

```renpy
Копировать
Редактировать
menu:
    "What to do?":
        "Go left":
            if is_night:
                "It's pitch dark."
            else:
                "It's sunny outside."
```
The tool will detect both: "It's pitch dark.", "It's sunny outside."

✅ Context-aware search:

- Stores info about conditions (if) and dialogue nesting level

✅ Visual editor:

- In-game UI to browse, inspect, and edit lines

✅ Hot editing:

- Changes apply immediately and can be saved to .rpy source

✅ Safe workflow:

- Backup system for original lines
- Inline tag validation with error messages

Currently WIP.
