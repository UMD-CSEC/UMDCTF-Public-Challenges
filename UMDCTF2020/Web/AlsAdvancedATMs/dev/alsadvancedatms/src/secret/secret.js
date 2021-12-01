import React from 'react';
import Table from 'react-bootstrap/Table';
function Secret() {
  return (
    <div className='center'>
      <h1>Super Secret Database</h1>
      <Table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Password</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>root</td>
            <td>dG9vcg==</td>
          </tr>
          <tr>
            <td>admin</td>
            <td>YWRtaW4=</td>
          </tr>
          <tr>
            <td>user</td>
            <td>cGFzc3dvcmQ=</td>
          </tr>
          <tr>
            <td>umd-csec</td>
            <td>VU1EQ1RGLXtvcDNuX2RAdEBfYjY0X2JAZH0=</td>
          </tr>
          <tr>
          <td>AzureDiamond</td>
          <td>SHVudGVyMg==</td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default Secret;
