import dataclasses
import fasthtml.common as fh
import models.local_config
import version

head_elements = (
    fh.Meta(charset='utf-8'),
    fh.Meta(name='viewport', content='width=device-width, initial-scale=1, shrink-to-fit=no'),
    fh.Link(rel='stylesheet', href='/static/bootstrap-5.3.3.css'),
    fh.Link(rel='stylesheet', href='/static/bootstrap-icons-1.11.3.css'),
)


default_scripts = (
    fh.Script(src='/static/bootstrap-5.3.3.bundle.js'),
    fh.Script(src='/static/htmx-2.0.4.js'),
)


def get_local_config(req: fh.Request, sess):
    req.state.local_config = models.local_config.LocalConfig(models.local_config.get_local_config_path())


def check_bootstrap_configuration(req: fh.Request, sess):
    openid_client_id = req.state.local_config.openid_client_id
    openid_client_secret = req.state.local_config.openid_client_secret
    if openid_client_id is None or openid_client_secret is None:
        return fh.RedirectResponse('/bootstrap', status_code=303)


before = (
    fh.Beforeware(get_local_config),
    fh.Beforeware(check_bootstrap_configuration, skip=['/bootstrap', '/static/.*']),
)


@dataclasses.dataclass
class BasePage:
    content: tuple

    def __ft__(self):
        elements = (NavRow(),) + self.content + (FootRow(),)
        return (
            fh.Div(
                *elements,
                cls='container-fluid'
            ),
            *default_scripts
        )


class BootstrapForm:
    @staticmethod
    def __ft__():
        return fh.Form(
            fh.Fieldset(
                fh.Legend('OpenID configuration'),
                fh.Div(
                    fh.Label('OpenID client ID', cls='form-label', _for='openid/client-id'),
                    fh.Input(cls='form-control', id='openid/client-id', name='openid/client-id', required=True,
                             type='text'),
                    cls='mb-3'
                ),
                fh.Div(
                    fh.Label('OpenID client secret', cls='form-label', _for='openid/client-secret'),
                    fh.Input(cls='form-control', id='openid/client-secret', name='openid/client-secret', required=True,
                             type='password'),
                    cls='mb-3'
                )
            ),
            fh.Fieldset(
                fh.Legend('Administration'),
                fh.Div(
                    fh.Label('Administrator email address', cls='form-label', _for='admin-email'),
                    fh.Input(cls='form-control', id='admin-email', name='admin-email', required=True, type='email'),
                    cls='mb-3'
                )
            ),
            fh.Button(
                'Submit',
                cls='btn btn-primary',
                type='submit',
            ),
            enctype='application/x-www-form-urlencoded',
            method='post'
        )


class BootstrapPage:
    @staticmethod
    def __ft__():
        return fh.Div(
            fh.Div(
                fh.Div(
                    fh.H1('Bootstrap configuration'),
                    fh.P('Please provide the following values to bootstrap this application.'),
                    BootstrapForm(),
                    cls='col-auto mx-auto'
                ),
                cls='pt-3 row'
            ),
            FootRow(),
            cls='container-fluid'
        )


@dataclasses.dataclass
class Breadcrumb:
    icon_class: str = 'bi-house-fill'
    text: str = 'Yavin'
    href: str = '#'

    def __ft__(self):
        return fh.A(
            fh.Strong(
                fh.I(cls=self.icon_class),
                f' {self.text}',
            ),
            cls='btn btn-outline-dark',
            href=self.href
        )


class FootRow:
    @staticmethod
    def __ft__():
        return fh.Div(
            fh.Div(
                fh.Hr(cls='border-light'),
                fh.Small(
                    version.version,
                    ' ',
                    fh.Span('xs', cls='d-inline d-sm-none'),
                    fh.Span('sm', cls='d-none d-sm-inline d-md-none'),
                    fh.Span('md', cls='d-none d-md-inline d-lg-none'),
                    fh.Span('lg', cls='d-none d-lg-inline d-xl-none'),
                    fh.Span('xl', cls='d-none d-xl-inline d-xxl-none'),
                    fh.Span('xxl', cls='d-none d-xxl-inline'),
                    cls='text-body-secondary',
                ),
                cls='col'
            ),
            cls='row pt-3 pb-2',
            id = 'footer-row'
        )


class IndexContent:
    @staticmethod
    def __ft__():
        return fh.Div(
            fh.Div(
                IndexLinkList(),
                cls='col'
            ),
            cls='pt-3 row'
        )


class IndexLinkList:
    @staticmethod
    def __ft__():
        return fh.Div(
            PageLink('Balances', '/balances'),
            PageLink('Billboard Hot 100 #1', '/billboard'),
            PageLink('Captain&#x02bc;s log', '/captains-log'),
            PageLink('Electricity', '/electricity'),
            PageLink('Expenses', '/expenses'),
            PageLink('Jar', '/jar'),
            PageLink('Library', '/library'),
            PageLink('Movie night', '/movie-night'),
            PageLink('Phone usage', '/phone'),
            PageLink('Tithing', '/tithing'),
            PageLink('Weight', '/weight'),
            cls='list-group'
        )


class IndexPage:
    @staticmethod
    def __ft__():
        return BasePage((IndexContent(),))


class NavRow:
    @staticmethod
    def __ft__():
        return fh.Nav(
            fh.Div(
                Breadcrumb(),
                cls='col-auto'
            ),
            fh.Div(
                SignInControl(),
                cls='col-auto ms-auto'
            ),
            cls='pt-3 row',
            id = 'nav-row'
        )


@dataclasses.dataclass
class PageLink:
    link_text: str
    href: str

    def __ft__(self):
        return fh.A(
            fh.NotStr(self.link_text),
            cls='list-group-item list-group-item-action',
            href=self.href
        )


class SignInControl:
    @staticmethod
    def __ft__():
        return fh.A(
            fh.I(cls='bi-person-fill'),
            ' Sign in',
            cls='btn btn-primary',
            href='#'
        )
