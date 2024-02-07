import {
  Avatar,
  Box,
  Button,
  IconButton,
  Popper,
  styled,
  TextField,
} from '@mui/material';
import React from 'react';
import Icon from '@mui/material/Icon';
import {QWebChannel} from 'qwebchannel';


const Widget = styled('div')(({ theme, width }) => ({
  padding: 10,
  borderRadius: 3,
  width: 450,
  height: 200,
  maxWidth: '100%',
  margin: 'auto',
  position: 'relative',
  textAlign: 'right',
  zIndex: 1,
  backgroundColor:
    theme.palette.mode === 'dark' ? 'rgba(0,0,0,0.6)' : 'rgba(255,255,255,0.8)',
  // backdropFilter: 'blur(40px)',
}));

export default function DisplayCommandPopper({ virtualElButton, virtualElPopper }) {
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const [displayed, setDisplayed] = React.useState(false);
  const [value, setValue] = React.useState("");
  const [widgetWidth, setWidgetWidth] = React.useState(Math.floor(window.innerWidth/2));

  React.useEffect(() => {
    const onResize = () => setWidgetWidth(Math.floor(window.innerWidth/2))
    window.addEventListener('resize', onResize);
  }, []);

  const theme = {
    spacing: 8,
  }

  return (
    <div>
      <Popper open={displayed} anchorEl={virtualElPopper}>
        <Widget width={widgetWidth} >
          <TextField
            id="outlined-multiline-static"
            label="JS command"
            multiline
            rows={5}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            sx={{ 
              width: 450,
            }}
          />
          <Button
            color="secondary"
            variant="contained"
            onClick={() => {eval(value)}}
            sx={{
              mt: 1,
            }}
          >
            Execute
          </Button>
        </Widget>
      </Popper>
      <Popper open={true} anchorEl={virtualElButton}>
        <Avatar sx={{ bgcolor: 'rgba(152, 152, 152, 0.3)' }} style={{ border: '0.1px solid rgba(3, 200, 255, 0.5)' }}>
          <IconButton color="primary" onClick={() => {
            setDisplayed(!displayed);;
          }}><Icon>terminal</Icon></IconButton>
        </Avatar>
      </Popper>
    </div>
  );
}