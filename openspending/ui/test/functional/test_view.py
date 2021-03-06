import json

from .. import ControllerTestCase, url, helpers as h
from openspending.model import View, Dataset


class TestViewController(ControllerTestCase):

    def setup(self):
        super(TestViewController, self).setup()
        self.user = h.make_account('test')
        h.load_fixture('cra', self.user)
        #h.clean_and_reindex_solr()

    def test_index(self):
        response = self.app.get(url(controller='view',
            action='index', dataset='cra'),
            extra_environ={'REMOTE_USER': 'test'})
        assert 'Library of visualisations' in response.body

    def test_delete(self):
        # TODO: Create the view using a fixture
        self.app.post(url(controller='view', action='create',
                                    dataset='cra'),
                        params={'widget': 'treemap',
                                'label': 'I am a banana!',
                                'state': '{"foo":"banana"}'},
                        extra_environ={'REMOTE_USER': 'test'})
        response = self.app.delete(url(controller='view',
            action='delete', dataset='cra', name='i-am-a-banana'),
            extra_environ={'REMOTE_USER': 'test'})
        dataset = Dataset.by_name('cra')
        view = View.by_name(dataset, 'i-am-a-banana')
        assert view is None
        assert '302' in response.status

    def test_delete_by_unauthorized_user(self):
        # TODO: Create the view using a fixture
        self.app.post(url(controller='view', action='create',
                                    dataset='cra'),
                        params={'widget': 'treemap',
                                'label': 'I am a banana!',
                                'state': '{"foo":"banana"}'},
                        extra_environ={'REMOTE_USER': 'test'})
        response = self.app.delete(url(controller='view',
            action='delete', dataset='cra', name='i-am-a-banana'),
            expect_errors=True,
            extra_environ={'REMOTE_USER': 'unauthorized_user'})
        dataset = Dataset.by_name('cra')
        view = View.by_name(dataset, 'i-am-a-banana')
        assert view is not None
        assert '403' in response.status

    def test_new(self):
        response = self.app.get(url(controller='view',
            action='new', dataset='cra'),
            extra_environ={'REMOTE_USER': 'test'})
        assert 'widgets.js' in response.body

    def test_create_noauth(self):
        response = self.app.post(url(controller='view', action='create',
                                    dataset='cra'),
                        params={'widget': 'treemap',
                                'label': 'I am a banana!',
                                'state': '{"foo":"banana"}'},
                        expect_errors=True)
        assert '403' in response.status, response.status

    def test_create(self):
        response = self.app.post(url(controller='view', action='create',
                                    dataset='cra'),
                        params={'widget': 'treemap',
                                'label': 'I am a banana!',
                                'state': '{"foo":"banana"}'},
                        extra_environ={'REMOTE_USER': 'test'})
        assert '302' in response.status, response.status
        assert '/cra/views/i-am-a-banana' in response.headers.get('location'), \
            response.headers

        response = self.app.get(url(controller='view', action='view',
                                    dataset='cra', name='i-am-a-banana',
                                    format='json'))
        data = json.loads(response.body)
        assert data['widget']=='treemap', data

        response = self.app.get(url(controller='view', action='view',
                                    dataset='cra', name='i-am-a-banana'))
        assert 'title>I am a banana!' in response.body, response

    def test_embed(self):
        response = self.app.get(url(controller='view', action='embed',
                                    dataset='cra'),
                        params={'widget': 'treemap'})
        assert u"Embedded" in response.body, response.body
        response = self.app.get(url(controller='view', action='embed',
                                    dataset='cra'),
            expect_errors=True)
        assert "400" in response.status, response.status

    def test_embed_state(self):
        response = self.app.get(url(controller='view', action='embed',
                                    dataset='cra'),
                        params={'widget': 'treemap',
                                'state': '{"foo":"banana"}'})
        assert u"banana" in response.body, response.body
        response = self.app.get(url(controller='view', action='embed',
                                    dataset='cra'),
                        params={'widget': 'treemap',
                                'state': '{"foo:"banana"}'},
            expect_errors=True)
        assert "400" in response.status, response.status
