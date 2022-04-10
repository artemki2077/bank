from flaskr import app


def test_login():
    client = app.app.test_client()
    url = '/login'
    response = client.post(url, data=dict(
        username='artem',
        password='maxar2005'

    ), follow_redirects=True)
    assert b"All transactions with artem" in response.data