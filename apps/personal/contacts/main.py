import argparse
import logging
import pickle
import os
import vobject

ZPUI_HOME = "~/.zpui/"
SAVE_FILENAME = "contacts.pickle"


class AddressBook(object):
    # todo : encrypt ?
    def __init__(self):
        self.contacts = []
        self.load_from_file()

    def load_from_file(self):
        self.contacts = pickle.load(self.get_save_file_path())

    def save_to_file(self):
        pickle.dump(self.contacts, self.get_save_file_path())

    @staticmethod
    def get_save_file_path():
        return os.path.join(os.path.expanduser(ZPUI_HOME), SAVE_FILENAME)


class Contact(object):
    def __init__(self):
        self.name = []
        self.name = []
        self.address = []
        self.telephone = []
        self.email = []
        self.url = []
        self.note = []
        self.org = []
        self.photo = []
        self.title = []


class VCardContactConverter(object):
    vcard_mapping = {
        'fn': 'name',
        'n': 'name',
        'adr': 'address',
        'tel': 'telephone',
        'email': 'email',
        'url': 'url',
        'note': 'note',
        'org': 'org',
        'photo': 'photo',
        'title': 'title'
    }

    # list of content found in my file :
    # {'adr',
    #  'email',
    #  'fn',
    #  'n',
    #  'note',
    #  'org',
    #  'photo',
    #  'tel',
    #  'title',
    #  'url',
    #  'version',
    #  'x-android-custom',
    #  'x-phonetic-first-name'

    @staticmethod
    def to_zpui_contact(v_contact):
        # type: (vobject.base.Component) -> Contact
        contact = Contact()
        for key in v_contact.contents.keys():
            if key not in VCardContactConverter.vcard_mapping: continue
            attr = getattr(contact, VCardContactConverter.vcard_mapping[key])
            assert type(attr) == list
            attr += [v.value for v in v_contact.contents[key]]
        return contact

    @staticmethod
    def parse_contact_file(file_path):
        # type: (str) -> list
        file_content = VCardContactConverter.read_file_content(file_path)
        contacts = [c for c in vobject.readComponents(file_content, ignoreUnreadable=True)]
        logging.info("Found {} contact in file {}", len(contacts), file_path)
        return contacts

    @staticmethod
    def read_file_content(file_path):
        with open(file_path, 'r') as f:
            file_content = f.read()
            return file_content

    @staticmethod
    def load_contacts(contact_card_files):
        # type: (list) -> list
        contacts = []
        for file_path in contact_card_files:
            contacts += VCardContactConverter.parse_contact_file(file_path)
        logging.info("finished : {} contacts loaded", len(contacts))
        return contacts


def find_contact_files(folder):
    # type: (str) -> list(str)
    home = os.path.expanduser(folder)
    if not os.path.exists(home):
        os.mkdir(home)
    contact_card_files = [os.path.join(home, f) for f in os.listdir(home) if f.lower().endswith("vcf")]
    return contact_card_files


def store_contacts(contacts):
    # type: (list) -> None
    cts = [VCardContactConverter.to_zpui_contact(contact) for contact in contacts]



def load_vcf(folder):
    # type: (str) -> None
    contact_card_files = find_contact_files(folder)
    contacts = VCardContactConverter.load_contacts(contact_card_files)
    store_contacts(contacts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--src-folder', dest='src_folder', action='store', metavar="DIR",
                        help='Folder to read vcard from')
    args = parser.parse_args()

    load_vcf(args.src_folder)
