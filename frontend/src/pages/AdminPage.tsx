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
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
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

  const { data: analysesData } = useQuery({
    queryKey: ['admin-analyses-over-time'],
    queryFn: () => adminApi.getAnalysesOverTime(30).then((res) => res.data),
  })

  const { data: userGrowthData } = useQuery({
    queryKey: ['admin-user-growth'],
    queryFn: () => adminApi.getUserGrowth(30).then((res) => res.data),
  })

  const { data: topMoodsData } = useQuery({
    queryKey: ['admin-top-moods'],
    queryFn: () => adminApi.getTopMoods(10).then((res) => res.data),
  })

  if (statsLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    )
  }

  // Prepare chart data
  const analysesChartData = analysesData?.labels?.map((label: string, idx: number) => ({
    date: label,
    count: analysesData.values[idx],
  })) || []

  const userGrowthChartData = userGrowthData?.labels?.map((label: string, idx: number) => ({
    date: label,
    count: userGrowthData.values[idx],
  })) || []

  const topMoodsChartData = topMoodsData?.labels?.map((label: string, idx: number) => ({
    mood: label,
    count: topMoodsData.values[idx],
  })) || []

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

      {/* Analytics Charts */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Analytics
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Analyses Over Time */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analyses Over Time (Last 30 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analysesChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                  />
                  <YAxis />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" name="Analyses" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* User Growth */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Growth (Last 30 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={userGrowthChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                  />
                  <YAxis />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#82ca9d" name="Total Users" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Moods */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top 10 Most Popular Moods
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topMoodsChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mood" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#8884d8" name="Analysis Count" />
                </BarChart>
              </ResponsiveContainer>
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
