import components
import fasthtml.common as fh
import logging
import models.local_config

log = logging.getLogger(__name__)

def get_local_config() -> models.local_config.LocalConfig:
    return models.local_config.LocalConfig(models.local_config.get_local_config_path())


app = fh.FastHTML(
    before=components.before,
    default_hdrs=False,
    hdrs=components.head_elements,
    htmlkw={'lang': 'en'},
    secret_key=get_local_config().secret_key,
)


@app.route('/{fname:path}.{ext:static}')
def get(fname: str, ext: str):
    # relative to working directory
    return fh.FileResponse(f'hoth/{fname}.{ext}')


@app.route('/')
def get():
    return fh.Title('Yavin'), components.IndexPage()


@app.route('/bootstrap')
def get():
    return fh.Title('Bootstrap configuration'), components.BootstrapPage()


@app.route('/bootstrap')
async def post(req: fh.Request):
    async with req.form() as form:
        for k in form.keys():
            log.warning(f'{k}: {form.getlist(k)}')
        c = get_local_config()
        c.openid_client_id = form.get('openid/client-id')
        c.openid_client_secret = form.get('openid/client-secret')
        c.set_setting('admin-email', form.get('admin-email'))
    return fh.RedirectResponse('/', status_code=303)


@app.route('/ok')
def get():
    return fh.Section(
        fh.H1('Test'),
        fh.P('Hello World'),
        **{'epub:type': 'chapter'}
    )

fh.serve()
