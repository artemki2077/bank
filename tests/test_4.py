from flaskr import app

def test_login():
    client = app.app.test_client()
    url = '/login'
    response = client.post(url, data=dict(
        username='pop it',
        password='maxar2005'

    ), follow_redirects=True)
    assert b"All transactions with pop it" in response.data