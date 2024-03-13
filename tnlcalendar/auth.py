from nacl.signing import VerifyKey, SignedMessage
from nacl.encoding import HexEncoder, URLSafeBase64Encoder
from nacl.exceptions import BadSignatureError
from datetime import datetime
from flask import session

refrein_sig = "1b574123c473a629ce005c0e675b8ad3bd822246178e7c766b061803838bd1d5"

def refrein(auth):
    try:
        verify_key = VerifyKey(refrein_sig, encoder=HexEncoder)
        check_key = verify_key.verify(auth, encoder=URLSafeBase64Encoder)
    except BadSignatureError:
        return False
    except:
        return False

    if check_key:
        print('valid key!')
        msg = SignedMessage(check_key).decode('utf-8')
        user = msg.split(':')
        auth_time = datetime.fromtimestamp(int(user[1])) 
        now = datetime.now()

        diff = now - auth_time
        session['name'] = user[0]
        session['auth_time'] = user[1]

        print(session['name'])
        print(session['auth_time'])

        #if round(diff.total_seconds()) > 60:
        #    return False

        return True
    else:
        return False
