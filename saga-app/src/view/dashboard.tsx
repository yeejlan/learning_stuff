import { Tabs, Tab, Button } from 'react-bootstrap';


function Dashboard() {
  return (
<Tabs defaultActiveKey="home" id="uncontrolled-tab-example" className="mb-3">
  <Tab eventKey="home" title="Home">
    <Button style={{marginLeft: '10px'}} variant="primary">Primary</Button>
  </Tab>
  <Tab eventKey="profile" title="Profile">
    bbb
  </Tab>
  <Tab eventKey="contact" title="Contact">
    ccc
  </Tab>
</Tabs>
  );
}

export default Dashboard;