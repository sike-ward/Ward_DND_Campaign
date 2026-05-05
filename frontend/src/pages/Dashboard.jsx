import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SectionHeader from '@/components/SectionHeader';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { dashboard } from '@/api';

export default function Dashboard({ user }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, recentData] = await Promise.all([
          dashboard.stats(),
          dashboard.recent(),
        ]);
        setStats(statsData);
        setRecent(recentData);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const StatCard = ({ icon, label, value, color }) => (
    <Card
      accent={color}
      className="p-6 flex flex-col justify-between h-full"
    >
      <div>
        <div className="text-4xl mb-3">{icon}</div>
        <p className="text-txt-secondary text-sm font-medium">{label}</p>
      </div>
      <div className="text-3xl font-bold text-txt">
        {loading ? '—' : value}
      </div>
    </Card>
  );

  return (
    <div className="p-10 space-y-10">
      {/* Header */}
      <SectionHeader
        title="Dashboard"
        subtitle={`Welcome back, ${user?.username || 'Adventurer'} — here's your campaign at a glance.`}
      />

      {/* Stats Row */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard
          icon="📝"
          label="Notes"
          value={stats?.notes || 0}
          color="#8b5cf6"
        />
        <StatCard
          icon="📁"
          label="Folders"
          value={stats?.folders || 0}
          color="#10b981"
        />
        <StatCard
          icon="👤"
          label="Characters"
          value={stats?.characters || 0}
          color="#f59e0b"
        />
        <StatCard
          icon="⚔️"
          label="Quests"
          value={stats?.quests || 0}
          color="#ef4444"
        />
        <StatCard
          icon="🌌"
          label="Timeline"
          value={stats?.timeline_events || 0}
          color="#60a5fa"
        />
        <StatCard
          icon="🎲"
          label="Sessions"
          value={stats?.sessions || 0}
          color="#a78bfa"
        />
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-5 gap-5">
        {/* Recent Notes */}
        <div className="col-span-3">
          <Card className="p-6 h-full">
            <h3 className="text-lg font-bold text-txt mb-4">Recent Notes</h3>
            <div className="space-y-1">
              {loading ? (
                <p className="text-txt-muted text-sm">Loading...</p>
              ) : recent.length > 0 ? (
                recent.map((note) => (
                  <div
                    key={note.id}
                    onClick={() => navigate(`/browse?note=${note.id}`)}
                    className="px-4 py-3 rounded-lg hover:bg-hover cursor-pointer transition"
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-txt font-medium">{note.title}</span>
                      <span className="text-txt-muted text-xs">
                        {note.modified_date
                          ? new Date(note.modified_date).toLocaleDateString()
                          : 'N/A'}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-txt-muted text-sm">No notes yet</p>
              )}
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="col-span-2">
          <Card className="p-6 h-full">
            <h3 className="text-lg font-bold text-txt mb-4">Quick Actions</h3>
            <div className="space-y-3 flex flex-col h-full justify-center">
              <Button variant="primary" className="w-full" onClick={() => navigate('/create')}>
                New Note
              </Button>
              <Button variant="secondary" className="w-full" onClick={() => navigate('/browse')}>
                Browse Vault
              </Button>
              <Button variant="success" className="w-full" onClick={() => navigate('/chat')}>
                Ask AI
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
