import json

class LinkInfo():
    """
    Stores information on class links. 
    Data can be loaded via a JSON File using `.read_from_json`

    Args:
        name_ (str): The class' name
        link_ (str): Zoom (or other) link for the class
        day_ (str): What day the class takes place
        time_ (str): What time the class starts (Format as HH:MM 24hr)
    """
    @staticmethod
    def read_from_json(filepath) -> dict:
        """
        Load class data from a JSON file. See reference file for formatting

        Args:
            filepath (str): Path to the JSON file

        Returns:
            dict: Dictionary of all sets' class information
        """
        complete_dict = {}
        with open(filepath) as json_file:
            json_data = json.load(json_file)
        for set_ in json_data:
            tmp_list = []
            for class_ in set_["classes"]:
                tmp_list.append(LinkInfo(
                    class_["name"],
                    class_["link"],
                    class_["day"],
                    class_["time"],
                    class_["id"]
                ))
            complete_dict[set_["set"]] = tmp_list

        return complete_dict

    @staticmethod
    def save_to_json(filepath, list_links) -> None:
        complete_list = []
        for set_ in list_links:
            tmp_classes = []
            tmp_data = {}
            for class_ in list_links[set_]:
                tmp_classes.append(class_.to_dict())
            tmp_data["set"] = set_
            tmp_data["classes"] = tmp_classes
            complete_list.append(tmp_data)

        with open(filepath, 'w') as json_file:
            json.dump(complete_list, json_file, indent=4)

    def __init__(self, name_, link_, day_, time_, id_):
        self.id = id_
        self.name = name_
        self.url = link_
        self.day = day_
        self.time = time_

    def to_dict(self):
        class_dict = {
            "id": self.id,
            "name": self.name,
            "link": self.url,
            "day": self.day,
            "time": self.time
        }
        return class_dict