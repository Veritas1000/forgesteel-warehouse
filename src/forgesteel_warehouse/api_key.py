
class ApiKey:
    @staticmethod
    def makeApiKey(uid: int, key: str):
        if '$' in key:
            raise ValueError('UID and KEY must not contain "$"')
    
        return f"${uid}${key}"
    
    @staticmethod
    def parseApiKey(fullKey: str):
        split = fullKey.split('$')
        if len(split) != 3 or split[0] != '':
            raise ValueError('Malformed API Key')

        try:
            uid = int(split[1])
        except ValueError:
            raise ValueError('Malformed API Key')
        
        return (uid, split[2])
