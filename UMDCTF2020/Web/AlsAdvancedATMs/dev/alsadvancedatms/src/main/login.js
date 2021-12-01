import React, { Component } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import './css/login.css';

class Login extends Component {

  constructor(props) {
    super(props);
    this.state = {status: undefined, username: '', password: ''}
    this.submitForm = this.submitForm.bind(this)
    this.usernameChanged = this.usernameChanged.bind(this);
    this.passwordChanged = this.passwordChanged.bind(this);
  }

  submitForm(e) {
    e.preventDefault();
    this.setState({status: 'Invalid credentials'})
    this.setState({username: '', password: ''})
    setTimeout(this.removeStatus.bind(this), 2000)
  }

  usernameChanged(e) {
    this.setState({username: e.target.value})
  }

  passwordChanged(e) {
    this.setState({password: e.target.value})
  }

  removeStatus() {
    this.setState({status: undefined})
  }

  render() {
    return (
      <div>
        <h3>Login to your account</h3>
        <Form id='login-form' onSubmit={this.submitForm}>
          <Form.Label>Username</Form.Label>
          <Form.Control type='text' value={this.state.username} onChange={this.usernameChanged}/>
          <Form.Label>Password</Form.Label>
          <Form.Control type='password' value={this.state.password} onChange={this.passwordChanged}/>
          <Button variant='primary' type='submit'>Submit</Button>
        </Form>
        <h4>{this.state.status}</h4>
      </div>
    );
  }
}

export default Login;
