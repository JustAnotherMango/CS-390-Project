'use client';

import React, { useState, useEffect } from 'react';

interface Politician {
  id: number;
  politician: string;
  traded_issuer: string;
  ticker: string;
  published_date: string;
  trade_date: string;
  gap_unit: string;
  gap: string;
  trade_type: string;
  trade_size: string;
  page: number;
}

const PoliticianSearch: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [politicians, setPoliticians] = useState<Politician[]>([]);
  const [filteredPoliticians, setFilteredPoliticians] = useState<Politician[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPoliticians = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:5000/Politicians');
        const data = await response.json();
        setPoliticians(data);
        setFilteredPoliticians(data);
      } catch (error) {
        console.error('Error fetching politicians:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPoliticians();
  }, []);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);

    if (term.trim() === '') {
      setFilteredPoliticians(politicians);
    } else {
      const filtered = politicians.filter((p) =>
        p.politician.toLowerCase().includes(term.toLowerCase())
      );
      setFilteredPoliticians(filtered);
    }
  };

  return (
    <div>
      <h2>Politician Search</h2>
      <input
        type="text"
        placeholder="Search by politician name..."
        value={searchTerm}
        onChange={handleSearch}
        style={{ padding: '8px', width: '300px', marginBottom: '20px' }}
      />
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {filteredPoliticians.map((p) => (
            <li key={p.id}>
              <strong>{p.politician}</strong> &mdash; {p.ticker} &mdash; {p.trade_type} &mdash; {p.trade_size}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PoliticianSearch;
