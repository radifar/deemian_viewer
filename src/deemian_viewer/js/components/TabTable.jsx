import {
  Box,
  Button,
  Tab,
  Table,
  TableBody,
  TableCell,
  tableCellClasses,
  TableContainer,
  TableHead,
  TableRow,
  styled,
} from '@mui/material';
import { TabContext, TabList, TabPanel } from '@mui/lab';
import React from 'react';


const Widget = styled('div')(({ theme }) => ({
  padding: 5,
  borderRadius: 5,
  width: 600,
  height: 320,
  maxWidth: '100%',
  margin: 'auto',
  // position: 'relative',
  zIndex: 1,
  backgroundColor:
    theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.6)' : 'rgba(100,100,100,0.6)',
  // backdropFilter: 'blur(40px)',
}));

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    backgroundColor: 'rgba(33, 33, 33, 1)',
    textAlign: 'center',
    color: theme.palette.common.white,
  },
  [`&.${tableCellClasses.body}`]: {
    backgroundColor: 'rgba(40, 40, 40, 0.6)',
    fontSize: 13.5,
    padding: 2,
    mx: 0,
    textAlign: 'center',
    color: 'rgba(255, 255, 255, 1)',
  },
}));

const StyledTab = styled(Tab)(({ theme }) => ({
  px: 0.5,
  py: -1,
  minHeight: 16,
  textTransform :"none", 
  color: 'rgba(255, 255, 255, 0.8)',
  '&.Mui-selected': { color: 'rgba(255, 255, 255, 1)',
      textShadow: '2px 2px 4px rgba(0, 0, 0, 1), -2px -2px 4px rgba(0, 0, 0, 1)', },
}));


export default function TabTable({ tableData }) {
  const [, forceUpdate] = React.useReducer(x => x + 1, 0);
  const [value, setValue] = React.useState('0');

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const setupUpdate = () => {
    setValue('0')
    forceUpdate();
  }
  
  return (
    <Widget>
      <TabContext value={value}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <TabList variant="scrollable"
                onChange={handleChange}
                aria-label="lab API tabs example"
                sx={{ padding: 0, minHeight: 28 }} >
            {tableData.map((table, index) => (
              <StyledTab key={table.name} label={table.name} value={"" + index}/>
            ))}
          </TabList>
        </Box>
        {tableData.map((table, index) => (
        <TabPanel key={table.name} value={"" + index} sx={{ padding:0 }}>
          <TableContainer sx={{
              height: 275,
              "&::-webkit-scrollbar": {
                width: 8
              },
              "&::-webkit-scrollbar-track": {
                backgroundColor: 'rgba(255,255,255,0.2)'
              },
              "&::-webkit-scrollbar-thumb": {
                backgroundColor: 'rgba(33, 33, 33, 0.95)',
                borderRadius: 2
              }
            }}>
            <Table stickyHeader sx={{ minWidth: 450 }} size="small" aria-label="a dense table">
              <TableHead>
                <TableRow>
                  <StyledTableCell width="15"></StyledTableCell>
                  <StyledTableCell>id 1</StyledTableCell>
                  <StyledTableCell>atom 1 info</StyledTableCell>
                  <StyledTableCell>id 2</StyledTableCell>
                  <StyledTableCell>atom 2 info</StyledTableCell>
                  <StyledTableCell>distance</StyledTableCell>
                  <StyledTableCell>type</StyledTableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {table.current_data.map((row) => (
                  <TableRow
                    key={row[0]}
                    sx={{ 
                      '&:last-child td, &:last-child th': { border: 0 },
                      textShadow: '1px 1px 2px rgba(0, 0, 0, 0.6), -1px -1px 2px rgba(0, 0, 0, 0.6)',
                  }}
                  >
                    <StyledTableCell component="th" scope="row">
                      {row[0]}
                    </StyledTableCell>
                    <StyledTableCell align="right">{row[1]}</StyledTableCell>
                    <StyledTableCell align="right">{row[2]}</StyledTableCell>
                    <StyledTableCell align="right">{row[3]}</StyledTableCell>
                    <StyledTableCell align="right">{row[4]}</StyledTableCell>
                    <StyledTableCell align="right">{row[5].toFixed(3)}</StyledTableCell>
                    <StyledTableCell align="right">{row[6]}</StyledTableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
            ))}
      </TabContext>
      
      <Button id='tabforceUpdate' sx={{ display: 'none' }} onClick={setupUpdate}></Button>
    </Widget>
  );
}
