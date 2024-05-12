import os.path
import re
import urllib.parse

import aiohttp
from izihawa_textutils.regex import DOI_REGEX


class ApiUploader:
    def __init__(self, nexus_user_id: str | int, nexus_auth_token: str):
        self._nexus_user_id = str(nexus_user_id)
        self._nexus_auth_token = nexus_auth_token
        self._session = aiohttp.ClientSession()

    async def guess_external_id(self, file_path: str) -> str | None:
        base_name = os.path.basename(file_path)
        rsplitted = base_name.rsplit('.', 1)
        if len(rsplitted) < 2:
            raise ValueError('`file_path` should be a proper file with extension')
        file_name = rsplitted[0]
        # Elsevier
        if file_name.startswith('1-s2.0'):
            alternative_id = file_name[7:-10]
            async with self._session as session:
                crossref_response = await session.get(f'https://api.crossref.org/works/?filter=alternative-id:{alternative_id}')
                meta = await crossref_response.json()
                if meta['message']['items']:
                    return meta['message']['items'][0]['DOI']
        unquoted_file_name = urllib.parse.quote(file_path)
        if re.match(file_name, DOI_REGEX):
            return unquoted_file_name

    async def upload_file(self, file_path: str, external_id: str = None):
        if not external_id:
            external_id = await self.guess_external_id(file_path)
        if not external_id:
            raise ValueError("Can't figure out the DOI")
        form_data = aiohttp.FormData()
        form_data.add_field(
            'file',
            open(file_path, 'rb'),
            filename=urllib.parse.quote(external_id) + '.pdf',
        )
        form_data.add_field(
            'query',
            external_id,
        )
        async with self._session as session:
            await session.post(
                'https://api.libstc.cc/upload/',
                headers={
                    'X-Nexus-User-Id': self._nexus_user_id,
                    'X-Nexus-Auth-Token': self._nexus_auth_token,
                },
                data=form_data,
            )
