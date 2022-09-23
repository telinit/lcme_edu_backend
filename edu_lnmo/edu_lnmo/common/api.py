from ninja import Router

router = Router()


@router.get('/')
def list_events(request):
    return []