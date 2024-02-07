import {
  Avatar,
  IconButton,
  Popper,
} from '@mui/material';
import React from 'react';
import TabTable from './TabTable.jsx';
import Icon from '@mui/material/Icon';

export default function DisplayTablePopper({rows, tableData, virtualElButton, virtualElTable}) {
  
  const [displayed, setDisplayed] = React.useState(false);
  return (
    <div>
      <Popper id='data-table' open={displayed} anchorEl={virtualElTable}>
        <TabTable rows={rows} tableData={tableData} />
      </Popper>
      <Popper id='table-button' open={true} anchorEl={virtualElButton}>
        <Avatar sx={{ bgcolor: 'rgba(152, 152, 152, 0.3)' }} style={{ border: '0.1px solid rgba(3, 200, 255, 0.5)' }}>
          <IconButton color="primary" onClick={() => {
            setDisplayed(!displayed);;
          }}
          ><Icon>table_view</Icon></IconButton>
        </Avatar>
      </Popper>
    </div>
  );
}