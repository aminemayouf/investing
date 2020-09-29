import gettext

class Translator(object):
    def __init__(self, language):
        _ = gettext.gettext
        if not language == 'en':
            if language == 'fr':
                fr = gettext.translation('fr_FR', localedir='locales', languages=['fr'])
                fr.install()
                _ = fr.gettext
            else:
                print(_('The specified language was not found, the default language will be used'))
        self.translate = _

    def __call__(self, text):
        return self.translate(text)
