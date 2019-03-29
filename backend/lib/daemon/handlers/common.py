from lib.daemon import context

def handle_ping():
    return {'clients': len(context.accounts)}
