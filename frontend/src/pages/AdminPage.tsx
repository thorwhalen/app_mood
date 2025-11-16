import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material'
import { adminApi } from '@/services/api'

export default function AdminPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => adminApi.getStats().then((res) => res.data),
  })

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.getUsers().then((res) => res.data),
  })

  if (statsLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      <Typography variant="body1" paragraph>
        System management and user statistics.
      </Typography>

      {/* System Stats */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        System Statistics
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Users
              </Typography>
              <Typography variant="h4">{stats?.total_users || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Moods
              </Typography>
              <Typography variant="h4">{stats?.total_moods || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Analyses
              </Typography>
              <Typography variant="h4">{stats?.total_analyses || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Analyses Today
              </Typography>
              <Typography variant="h4">{stats?.analyses_today || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Users Table */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Users
      </Typography>
      {usersLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : users && users.length > 0 ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Email</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Moods</TableCell>
                <TableCell>Analyses</TableCell>
                <TableCell>Usage (Analyses)</TableCell>
                <TableCell>Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user: any) => (
                <TableRow key={user.id}>
                  <TableCell>
                    {user.email}
                    {user.is_superuser && (
                      <Chip label="Admin" size="small" color="primary" sx={{ ml: 1 }} />
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.is_active ? 'Active' : 'Inactive'}
                      color={user.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{user.moods_count}</TableCell>
                  <TableCell>{user.analyses_count}</TableCell>
                  <TableCell>
                    {user.analyses_used} / {user.analyses_limit}
                  </TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Alert severity="info">No users found.</Alert>
      )}
    </Box>
  )
}
