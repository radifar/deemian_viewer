import {
  Avatar,
  IconButton,
  Popper,
} from '@mui/material';
import React from 'react';
import Icon from '@mui/material/Icon';
import {QWebChannel} from 'qwebchannel';

export default function OpenButton({ virtualElButton, socket }) {
  const backendOpen = function()
    {
      new QWebChannel(socket, function(channel) {
        var backend = channel.objects.backend
        backend.openFile();
      });
    }

  return (
    <div>
      <Popper open={true} anchorEl={virtualElButton}>
        <Avatar sx={{ bgcolor: 'rgba(152, 152, 152, 0.3)' }} style={{ border: '0.1px solid rgba(3, 200, 255, 0.5)' }}>
          <IconButton color="primary" onClick={backendOpen}><Icon>folder_open</Icon></IconButton>
        </Avatar>
      </Popper>
    </div>
  );
}