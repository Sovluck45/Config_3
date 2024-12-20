import json
import re
import argparse


class ConfigParser:
    def __init__(self):
        self.data = {}

    def parse(self, text):
        text = self.remove_comments(text)
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if '<-' in line:
                self.parse_assignment(line)
            else:
                raise ValueError(f"Некорректная строка: {line}")

    def remove_comments(self, text):
        text = re.sub(r'\(comment.*?\)', '', text, flags=re.DOTALL)
        lines = text.splitlines()
        lines = [line for line in lines if not line.strip().startswith("#")]
        return "\n".join(lines)

    def parse_assignment(self, line):
        name, value = line.split('<-')
        name = name.strip()
        value = self.parse_value(value.strip())
        self.data[name] = value

    def parse_value(self, value):
        value = value.strip()
        if value == "true":
            return True
        elif value == "false":
            return False
        elif value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        elif value.isdigit():
            return int(value)
        elif re.match(r"^\d+\.\d+$", value):
            return float(value)
        elif value.startswith("{") and value.endswith("}"):
            return [self.parse_value(v.strip()) for v in value[1:-1].split(',') if v.strip()]
        elif value.startswith("$[") and value.endswith("]"):
            return self.parse_nested_dict(value[2:-1].strip())
        else:
            raise ValueError(f"Некорректное значение: {value}")

    def parse_nested_dict(self, text):
        if not text:
            return {}
        items = self.split_dict_items(text)
        result = {}
        for item in items:
            if ':' not in item:
                raise ValueError(f"Некорректный формат словаря: {item}")
            key, value = item.split(':', 1)
            result[key.strip()] = self.parse_value(value.strip())
        return result

    def split_dict_items(self, text):
        items = []
        depth = 0
        current_item = []
        in_string = False
        for char in text:
            if char == '"' and (not current_item or current_item[-1] != '\\'):
                in_string = not in_string
            if not in_string:
                if char == '[':
                    depth += 1
                elif char == ']':
                    depth -= 1
                elif char == ',' and depth == 0:
                    items.append(''.join(current_item).strip())
                    current_item = []
                    continue
            current_item.append(char)
        if current_item:
            items.append(''.join(current_item).strip())
        return items

    def to_json(self, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Конвертер конфигурационного языка в JSON.")
    parser.add_argument("input_file", help="Путь к входному файлу конфигурационного языка.")
    parser.add_argument("output_file", help="Путь к выходному JSON-файлу.")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()

        config_parser = ConfigParser()
        config_parser.parse(input_text)
        config_parser.to_json(args.output_file)
        print(f"Конвертация завершена. Результат сохранен в {args.output_file}")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
