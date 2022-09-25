from ninja import Router, Schema

router = Router()

class FileIO(Schema):
    pass

@router.get('/')
def list_events(request):
    return []