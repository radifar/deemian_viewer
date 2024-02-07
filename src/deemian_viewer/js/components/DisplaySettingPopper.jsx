import {
  Avatar,
  Box,
  Grid,
  IconButton,
  Popper,
  Slider,
  Typography,
} from '@mui/material';
import React from 'react';
import Icon from '@mui/material/Icon';

export default function DisplaySettingPopper({ virtualElButton, virtualElPopper }) {
  const [displayed, setDisplayed] = React.useState(false);
  const [value, setValue] = React.useState(70);

  const handleChange = (event, newValue) => {
    setValue(newValue);
    stage.setParameters({ fogFar: value})
  };
  
  const theme = {
    spacing: 8,
  }

  return (
    <div>
      <Popper open={displayed} anchorEl={virtualElPopper}>
        <Box component="section" sx={{
          py: 1,
          width: 180,
          height: 60,
          bgcolor: 'rgba(1, 80, 162, 0.1)',
          // border: '0.1px solid rgba(3, 200, 255, 0.5)',
          borderRadius: 3,
          fontSize: '0.700rem',
          fontWeight: '600',
        }}>
          <Grid container spacing={0}>
            <Grid item xs={1}></Grid>
            <Grid item xs={11}>
              <Typography id="fog-density" sx={{ color: 'rgba(255, 255, 255, 0.8)' }} gutterBottom>
                visibility range
              </Typography>
            </Grid>
            <Grid item xs={1}></Grid>
            <Grid item xs={11}>
              <Slider
                aria-label="Far fog"
                size="small"
                sx = {{ pt: 0, width: 150}}
                min={51}
                max={90}
                value={value}
                onChange={handleChange} />
            </Grid>
          </Grid>
          
          
        </Box>
      </Popper>
      <Popper open={true} anchorEl={virtualElButton}>
        <Avatar sx={{ bgcolor: 'rgba(152, 152, 152, 0.3)' }} style={{ border: '0.1px solid rgba(3, 200, 255, 0.5)' }}>
          <IconButton color="primary" onClick={() => {
            setDisplayed(!displayed);;
          }}><Icon>tune</Icon></IconButton>
        </Avatar>
      </Popper>
    </div>
  );
}