'use strict';
import React from "react";
import {Card, Col, Nav, Row, Tab} from "react-bootstrap";
import ProfileForm from "./ProfileForm";
import ChangePasswordForm from "./ChangePasswordForm";
import SocialLinksForm from "./SocialLinksForm";
import {FormattedMessage as Msg} from "react-intl";


export default class Profile extends React.Component {
  constructor(props) {
    super(props);
    this.defaultTab = window.location.hash || '#main';
  }

  render() {
    return <Tab.Container defaultActiveKey={this.defaultTab}>
      <Row>
        <Col md={3} sm={3} lg={2}>
          <Nav className="flex-column" variant="pills">
            <Nav.Item><Nav.Link eventKey="#main"><Msg id="profile"/></Nav.Link></Nav.Item>
          </Nav>
        </Col>
        <Col md={9} sm={9} lg={10}>
          <Tab.Content>
            <Tab.Pane eventKey="#main">
              <Card className="my-2">
                <Card.Header><Msg id="publicProfile"/></Card.Header>
                <Card.Body>
                  <ProfileForm fields={this.props.user}/>
                </Card.Body>
              </Card>
              <Card className="my-2">
                <Card.Header><Msg id="changePassword"/></Card.Header>
                <Card.Body>
                  <ChangePasswordForm/>
                </Card.Body>
              </Card>
              <Card className="my-2">
                <Card.Header><Msg id="socialProfile"/></Card.Header>
                <Card.Body>
                  <SocialLinksForm providers={this.props.providers}/>
                </Card.Body>
              </Card>
            </Tab.Pane>
          </Tab.Content>
        </Col>
      </Row>
    </Tab.Container>;
  }
}
