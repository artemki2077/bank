from flaskr import app


def test_login():
    client = app.app.test_client()
    url = '/login'
    response = client.post(url, data=dict(
        username='ley',
        password='123'
    ))
    assert b'Invalid' in response.data