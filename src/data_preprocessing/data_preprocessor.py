from models.message_models import DialogData

class DataPreprocessor:
    """Class for preprocessing dialog data."""

    def __init__(self):
        """Initialize the DataPreprocessor."""
        pass

    def _read_csv(self, data_path: str) -> DialogData:
        """Reads dialog data from a CSV file.

        Args:
            data_path: The path to the CSV file.

        Returns:
            The DialogData object created from the CSV file.
        """
        pass

    def _read_json(self, data_path: str) -> DialogData:
        """Reads dialog data from a JSON file.

        Args:
            data_path: The path to the JSON file.

        Returns:
            The DialogData object created from the JSON file.
        """
        pass

    def _read_text(self, data_path: str) -> DialogData:
        """Reads dialog data from a text file.

        Args:
            data_path: The path to the text file.

        Returns:
            The DialogData object created from the text file.
        """
        pass

    def clean_data(self, dialog_data: DialogData) -> DialogData:
        """Cleans the dialog data.

        Args:
            dialog_data: The DialogData object to clean.

        Returns:
            The cleaned DialogData object.
        """
        pass
    
    def preprocess(self, data_path: str) -> DialogData:
        """
        Preprocesses the dialog data. The input `dialog_data` object can be
        created from various file formats like JSON, text files, etc.

        Args:
            data_path: The path to the dialog data file. The file format can be csv
                JSON, text files, etc.

        Returns:
            The preprocessed DialogData object.
        """
        print("Preprocessing data...")
