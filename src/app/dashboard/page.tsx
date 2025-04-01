import React from 'react';
import PoliticianSearch from '../../components/ui/PoliticianSearch';

export default function Home() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>My Dashboard</h1>
      <PoliticianSearch />
    </div>
  );
}
