import React, { useState, useEffect, useCallback } from 'react';
import { Memory } from '../types/chat';

interface MemoryManagerProps {
  userId: string;
}

const MemoryManager: React.FC<MemoryManagerProps> = ({ userId }) => {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(false);
  const [newMemory, setNewMemory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  // Fetch memories
  const fetchMemories = useCallback(async (search?: string) => {
    setLoading(true);
    try {
      const url = search 
        ? `/api/memories/search/${userId}?query=${encodeURIComponent(search)}`
        : `/api/memories/${userId}`;
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setMemories(data.memories || []);
      }
    } catch (error) {
      console.error('Error fetching memories:', error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Add new memory
  const addMemory = async () => {
    if (!newMemory.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/memories/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          memory_text: newMemory,
          importance: 0.7
        })
      });
      
      if (response.ok) {
        setNewMemory('');
        setShowAddForm(false);
        fetchMemories(searchQuery);
      }
    } catch (error) {
      console.error('Error adding memory:', error);
    } finally {
      setLoading(false);
    }
  };

  // Delete memory
  const deleteMemory = async (memoryId: string) => {
    if (!window.confirm('Are you sure you want to delete this memory?')) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/memories/${userId}/${memoryId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchMemories(searchQuery);
      }
    } catch (error) {
      console.error('Error deleting memory:', error);
    } finally {
      setLoading(false);
    }
  };

  // Clear all memories
  const clearAllMemories = async () => {
    if (!window.confirm('Are you sure you want to clear ALL memories? This cannot be undone.')) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/memories/${userId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setMemories([]);
      }
    } catch (error) {
      console.error('Error clearing memories:', error);
    } finally {
      setLoading(false);
    }
  };

  // Search memories
  const handleSearch = () => {
    fetchMemories(searchQuery);
  };

  // Load memories on component mount
  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);

  return (
    <div className="memory-manager">
      <div className="memory-header">
        <h3>Memory Management</h3>
        <div className="memory-actions">
          <button 
            className="btn btn-primary" 
            onClick={() => setShowAddForm(!showAddForm)}
            disabled={loading}
          >
            {showAddForm ? 'Cancel' : 'Add Memory'}
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={clearAllMemories}
            disabled={loading}
          >
            Clear All
          </button>
        </div>
      </div>

      {/* Add Memory Form */}
      {showAddForm && (
        <div className="add-memory-form">
          <textarea
            value={newMemory}
            onChange={(e) => setNewMemory(e.target.value)}
            placeholder="Enter important information to remember..."
            className="input"
            rows={3}
          />
          <div className="form-actions">
            <button 
              className="btn btn-primary" 
              onClick={addMemory}
              disabled={!newMemory.trim() || loading}
            >
              {loading ? 'Adding...' : 'Add Memory'}
            </button>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="memory-search">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search memories..."
          className="input"
        />
        <button 
          className="btn btn-primary" 
          onClick={handleSearch}
          disabled={loading}
        >
          Search
        </button>
        {searchQuery && (
          <button 
            className="btn btn-secondary" 
            onClick={() => {
              setSearchQuery('');
              fetchMemories();
            }}
          >
            Clear Search
          </button>
        )}
      </div>

      {/* Memories List */}
      <div className="memories-list">
        {loading && <div className="loading">Loading memories...</div>}
        
        {!loading && memories.length === 0 && (
          <div className="no-memories">
            {searchQuery ? 'No memories found for this search.' : 'No memories stored yet.'}
          </div>
        )}
        
        {memories.map((memory, index) => (
          <div key={memory.id || index} className="memory-item">
            <div className="memory-content">
              <p>{memory.memory || memory.content}</p>
              {memory.metadata && (
                <div className="memory-metadata">
                  <small>
                    {memory.metadata.timestamp && 
                      new Date(memory.metadata.timestamp).toLocaleString()}
                    {memory.metadata.importance && 
                      ` • Importance: ${memory.metadata.importance}`}
                  </small>
                </div>
              )}
            </div>
            <div className="memory-actions">
              <button 
                className="btn btn-secondary" 
                onClick={() => deleteMemory(memory.id)}
                disabled={loading}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MemoryManager;
