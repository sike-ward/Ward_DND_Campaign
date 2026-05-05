import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import SectionHeader from '@/components/SectionHeader';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input, { TextArea } from '@/components/Input';
import Badge from '@/components/Badge';
import { notes, folders } from '@/api';

// ════════════════════════════════════════════════════════════════════════════
// Browse — Full vault browser with folder tree, editing, tags, metadata
// ════════════════════════════════════════════════════════════════════════════

export default function Browse() {
  const [searchParams] = useSearchParams();

  // ── Data ─────────────────────────────────────────────────────────────────
  const [allNotes, setAllNotes] = useState([]);
  const [allFolders, setAllFolders] = useState([]);
  const [loading, setLoading] = useState(true);

  // ── Selection & navigation ───────────────────────────────────────────────
  const [selectedNote, setSelectedNote] = useState(null); // full NoteDetail
  const [activeFolder, setActiveFolder] = useState(null); // folder id or null = "All"
  const [expandedFolders, setExpandedFolders] = useState(new Set());

  // ── Editing ──────────────────────────────────────────────────────────────
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');

  // ── Search ───────────────────────────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null); // null = not searching
  const searchTimeout = useRef(null);

  // ── Tag filter ───────────────────────────────────────────────────────────
  const [tagFilter, setTagFilter] = useState('');

  // ── New tag input ────────────────────────────────────────────────────────
  const [newTag, setNewTag] = useState('');

  // ── Create note/folder dialogs ───────────────────────────────────────────
  const [showCreateNote, setShowCreateNote] = useState(false);
  const [newNoteTitle, setNewNoteTitle] = useState('');
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  // ── Move note ────────────────────────────────────────────────────────────
  const [showMoveDialog, setShowMoveDialog] = useState(false);

  // ── Metadata editing ─────────────────────────────────────────────────────
  const [showMetaEditor, setShowMetaEditor] = useState(false);
  const [metaKey, setMetaKey] = useState('');
  const [metaValue, setMetaValue] = useState('');

  // ── Status ───────────────────────────────────────────────────────────────
  const [statusMsg, setStatusMsg] = useState('');

  // ════════════════════════════════════════════════════════════════════════
  // Data loading
  // ════════════════════════════════════════════════════════════════════════

  const loadData = async () => {
    try {
      const [notesList, foldersList] = await Promise.all([
        notes.list(),
        folders.list(),
      ]);
      setAllNotes(notesList);
      setAllFolders(foldersList);
    } catch (err) {
      console.error('Failed to load vault:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  // Auto-select note from URL query param (e.g. /browse?note=abc123)
  useEffect(() => {
    const noteId = searchParams.get('note');
    if (noteId && !loading && allNotes.length > 0 && !selectedNote) {
      handleSelectNote({ id: noteId });
    }
  }, [loading, allNotes, searchParams]);

  const flash = (msg) => {
    setStatusMsg(msg);
    setTimeout(() => setStatusMsg(''), 3000);
  };

  // ════════════════════════════════════════════════════════════════════════
  // Search (debounced, uses backend full-text search)
  // ════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(async () => {
      try {
        const data = await notes.search(searchQuery);
        setSearchResults(data.results || []);
      } catch {
        setSearchResults([]);
      }
    }, 300);
    return () => clearTimeout(searchTimeout.current);
  }, [searchQuery]);

  // ════════════════════════════════════════════════════════════════════════
  // Derived data
  // ════════════════════════════════════════════════════════════════════════

  // All unique tags across notes
  const allTags = [...new Set(allNotes.flatMap((n) => n.tags || []))].sort();

  // Notes to display (filtered by folder and tag)
  const displayNotes = (() => {
    if (searchResults) return searchResults;
    let list = allNotes;
    if (activeFolder) {
      list = list.filter((n) => n.folder_id === activeFolder);
    }
    if (tagFilter) {
      list = list.filter((n) =>
        (n.tags || []).some((t) => t.toLowerCase() === tagFilter.toLowerCase())
      );
    }
    return list;
  })();

  // Group notes by folder for tree display
  const notesByFolder = {};
  allNotes.forEach((n) => {
    const fid = n.folder_id || '__unfiled__';
    if (!notesByFolder[fid]) notesByFolder[fid] = [];
    notesByFolder[fid].push(n);
  });
  const unfiledNotes = notesByFolder['__unfiled__'] || [];

  // ════════════════════════════════════════════════════════════════════════
  // Note selection
  // ════════════════════════════════════════════════════════════════════════

  const handleSelectNote = async (noteItem) => {
    setIsEditing(false);
    setShowMetaEditor(false);
    try {
      const detail = await notes.get(noteItem.id);
      setSelectedNote(detail);
      setEditTitle(detail.title);
      setEditContent(detail.content || '');
    } catch (err) {
      console.error('Failed to load note:', err);
      flash('Failed to load note');
    }
  };

  // ════════════════════════════════════════════════════════════════════════
  // CRUD operations
  // ════════════════════════════════════════════════════════════════════════

  const handleSave = async () => {
    if (!selectedNote) return;
    try {
      const updated = await notes.update(selectedNote.id, {
        title: editTitle,
        content: editContent,
      });
      setSelectedNote(updated);
      setIsEditing(false);
      flash('Saved');
      await loadData();
    } catch (err) {
      flash('Failed to save: ' + err.message);
    }
  };

  const handleDelete = async () => {
    if (!selectedNote) return;
    if (!confirm(`Delete "${selectedNote.title}"? This cannot be undone.`)) return;
    try {
      await notes.delete(selectedNote.id);
      setSelectedNote(null);
      flash('Note deleted');
      await loadData();
    } catch (err) {
      flash('Failed to delete: ' + err.message);
    }
  };

  const handleCreateNote = async () => {
    if (!newNoteTitle.trim()) return;
    try {
      const created = await notes.create(newNoteTitle, '', activeFolder);
      setShowCreateNote(false);
      setNewNoteTitle('');
      flash('Note created');
      await loadData();
      await handleSelectNote(created);
    } catch (err) {
      flash('Failed to create note: ' + err.message);
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;
    try {
      await folders.create(newFolderName);
      setShowCreateFolder(false);
      setNewFolderName('');
      flash('Folder created');
      await loadData();
    } catch (err) {
      flash('Failed to create folder: ' + err.message);
    }
  };

  const handleDeleteFolder = async (folderId) => {
    const folder = allFolders.find((f) => f.id === folderId);
    if (!confirm(`Delete folder "${folder?.name}"? Notes inside will become unfiled.`)) return;
    try {
      await folders.delete(folderId);
      if (activeFolder === folderId) setActiveFolder(null);
      flash('Folder deleted');
      await loadData();
    } catch (err) {
      flash('Failed to delete folder: ' + err.message);
    }
  };

  // ════════════════════════════════════════════════════════════════════════
  // Tag operations
  // ════════════════════════════════════════════════════════════════════════

  const handleAddTag = async () => {
    if (!selectedNote || !newTag.trim()) return;
    try {
      const updated = await notes.addTag(selectedNote.id, newTag.trim());
      setSelectedNote(updated);
      setNewTag('');
      flash('Tag added');
      await loadData();
    } catch (err) {
      flash('Failed to add tag: ' + err.message);
    }
  };

  const handleRemoveTag = async (tag) => {
    if (!selectedNote) return;
    try {
      const updated = await notes.removeTag(selectedNote.id, tag);
      setSelectedNote(updated);
      flash('Tag removed');
      await loadData();
    } catch (err) {
      flash('Failed to remove tag: ' + err.message);
    }
  };

  // ════════════════════════════════════════════════════════════════════════
  // Move note
  // ════════════════════════════════════════════════════════════════════════

  const handleMoveNote = async (destFolderId) => {
    if (!selectedNote) return;
    try {
      await notes.move(selectedNote.id, destFolderId || null);
      setShowMoveDialog(false);
      flash('Note moved');
      const updated = await notes.get(selectedNote.id);
      setSelectedNote(updated);
      await loadData();
    } catch (err) {
      flash('Failed to move: ' + err.message);
    }
  };

  // ════════════════════════════════════════════════════════════════════════
  // Metadata operations
  // ════════════════════════════════════════════════════════════════════════

  const handleAddMeta = async () => {
    if (!selectedNote || !metaKey.trim()) return;
    try {
      const updated = await notes.updateMeta(selectedNote.id, {
        [metaKey.trim()]: metaValue,
      });
      setSelectedNote(updated);
      setMetaKey('');
      setMetaValue('');
      flash('Metadata updated');
    } catch (err) {
      flash('Failed to update metadata: ' + err.message);
    }
  };

  const handleRemoveMeta = async (key) => {
    if (!selectedNote) return;
    try {
      const updated = await notes.updateMeta(selectedNote.id, { [key]: '' });
      setSelectedNote(updated);
      flash('Metadata removed');
    } catch (err) {
      flash('Failed to remove metadata: ' + err.message);
    }
  };

  // ════════════════════════════════════════════════════════════════════════
  // Permissions
  // ════════════════════════════════════════════════════════════════════════

  const handleUpdatePermissions = async (newPerms) => {
    if (!selectedNote) return;
    try {
      const updated = await notes.update(selectedNote.id, { permissions: newPerms });
      setSelectedNote(updated);
      flash('Permissions updated');
    } catch (err) {
      flash('Failed to update permissions: ' + err.message);
    }
  };

  // ════════════════════════════════════════════════════════════════════════
  // Group assignment
  // ════════════════════════════════════════════════════════════════════════

  const handleSetGroup = async (groupId) => {
    if (!selectedNote) return;
    try {
      const updated = await notes.update(selectedNote.id, { group_id: groupId || null });
      setSelectedNote(updated);
      flash('Group updated');
    } catch (err) {
      flash('Failed to update group: ' + err.message);
    }
  };

  // ════════════════════════════════════════════════════════════════════════
  // Folder tree toggle
  // ════════════════════════════════════════════════════════════════════════

  const toggleFolder = (folderId) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(folderId)) next.delete(folderId);
      else next.add(folderId);
      return next;
    });
  };

  // ════════════════════════════════════════════════════════════════════════
  // Helper: word count
  // ════════════════════════════════════════════════════════════════════════

  const wordCount = (text) =>
    text ? text.trim().split(/\s+/).filter(Boolean).length : 0;

  // ════════════════════════════════════════════════════════════════════════
  // RENDER
  // ════════════════════════════════════════════════════════════════════════

  return (
    <div className="p-6 flex flex-col h-full gap-4">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className="flex justify-between items-start">
        <SectionHeader
          title="📖 Browse"
          subtitle="Explore and manage your vault."
        />
        <div className="flex gap-2 items-center">
          {statusMsg && (
            <span className="text-accent text-xs font-medium bg-accent/10 px-3 py-1.5 rounded-lg">
              {statusMsg}
            </span>
          )}
          <Button variant="primary" size="sm" onClick={() => setShowCreateNote(true)}>
            + Note
          </Button>
          <Button variant="secondary" size="sm" onClick={() => setShowCreateFolder(true)}>
            + Folder
          </Button>
        </div>
      </div>

      {/* ── Create dialogs ─────────────────────────────────────────────── */}
      {showCreateNote && (
        <Card className="p-4 flex gap-2 items-end">
          <div className="flex-1">
            <Input
              label="New Note Title"
              placeholder="My new note..."
              value={newNoteTitle}
              onChange={(e) => setNewNoteTitle(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreateNote()}
            />
          </div>
          <Button variant="primary" size="sm" onClick={handleCreateNote}>Create</Button>
          <Button variant="ghost" size="sm" onClick={() => setShowCreateNote(false)}>Cancel</Button>
        </Card>
      )}
      {showCreateFolder && (
        <Card className="p-4 flex gap-2 items-end">
          <div className="flex-1">
            <Input
              label="New Folder Name"
              placeholder="NPCs, Locations, etc..."
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreateFolder()}
            />
          </div>
          <Button variant="primary" size="sm" onClick={handleCreateFolder}>Create</Button>
          <Button variant="ghost" size="sm" onClick={() => setShowCreateFolder(false)}>Cancel</Button>
        </Card>
      )}

      {/* ── Main layout (3-panel) ──────────────────────────────────────── */}
      <div className="flex gap-4 flex-1 overflow-hidden min-h-0">

        {/* ════ LEFT PANEL — Folder tree + search ════════════════════════ */}
        <Card className="w-72 flex-shrink-0 flex flex-col overflow-hidden p-0">
          {/* Search bar */}
          <div className="p-3 border-b border-txt-muted/10">
            <input
              placeholder="Search notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-elevated rounded-lg px-3 py-2 text-sm text-txt border border-transparent focus:border-accent focus:outline-none transition placeholder:text-txt-muted"
            />
          </div>

          {/* Tag filter */}
          {allTags.length > 0 && (
            <div className="px-3 py-2 border-b border-txt-muted/10">
              <select
                value={tagFilter}
                onChange={(e) => setTagFilter(e.target.value)}
                className="w-full bg-elevated rounded-lg px-2 py-1.5 text-xs text-txt border border-transparent focus:border-accent focus:outline-none"
              >
                <option value="">All Tags</option>
                {allTags.map((t) => (
                  <option key={t} value={t}>{t} ({allNotes.filter((n) => (n.tags || []).includes(t)).length})</option>
                ))}
              </select>
            </div>
          )}

          {/* Tree area */}
          <div className="flex-1 overflow-y-auto p-2">
            {loading ? (
              <p className="text-txt-muted text-sm p-2">Loading...</p>
            ) : searchResults ? (
              /* Search results mode */
              <div className="space-y-0.5">
                <p className="text-txt-muted text-xs px-2 py-1 font-medium">
                  {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
                </p>
                {searchResults.map((n) => (
                  <NoteTreeItem
                    key={n.id}
                    note={n}
                    isSelected={selectedNote?.id === n.id}
                    onClick={() => handleSelectNote(n)}
                  />
                ))}
              </div>
            ) : (
              /* Folder tree mode */
              <div className="space-y-0.5">
                {/* All Notes button */}
                <button
                  onClick={() => setActiveFolder(null)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition ${
                    !activeFolder
                      ? 'bg-accent/10 text-accent font-semibold'
                      : 'text-txt hover:bg-hover'
                  }`}
                >
                  📋 All Notes ({allNotes.length})
                </button>

                {/* Folders */}
                {allFolders.map((folder) => {
                  const folderNotes = notesByFolder[folder.id] || [];
                  const isExpanded = expandedFolders.has(folder.id);
                  const isActive = activeFolder === folder.id;

                  return (
                    <div key={folder.id}>
                      <div className="flex items-center group">
                        <button
                          onClick={() => { toggleFolder(folder.id); setActiveFolder(folder.id); }}
                          className={`flex-1 text-left px-3 py-2 rounded-lg text-sm transition flex items-center gap-2 ${
                            isActive
                              ? 'bg-accent/10 text-accent font-semibold'
                              : 'text-txt hover:bg-hover'
                          }`}
                        >
                          <span className="text-xs">{isExpanded ? '▼' : '▶'}</span>
                          <span>📁 {folder.name}</span>
                          <span className="text-txt-muted text-xs ml-auto">{folderNotes.length}</span>
                        </button>
                        <button
                          onClick={() => handleDeleteFolder(folder.id)}
                          className="hidden group-hover:block text-danger text-xs px-1 hover:bg-danger/10 rounded"
                          title="Delete folder"
                        >
                          ✕
                        </button>
                      </div>

                      {/* Notes inside folder */}
                      {isExpanded && folderNotes.length > 0 && (
                        <div className="ml-5 space-y-0.5">
                          {folderNotes.map((n) => (
                            <NoteTreeItem
                              key={n.id}
                              note={n}
                              isSelected={selectedNote?.id === n.id}
                              onClick={() => handleSelectNote(n)}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}

                {/* Unfiled notes */}
                {unfiledNotes.length > 0 && (
                  <div>
                    <button
                      onClick={() => { toggleFolder('__unfiled__'); setActiveFolder(null); }}
                      className="w-full text-left px-3 py-2 rounded-lg text-sm text-txt-muted hover:bg-hover transition flex items-center gap-2"
                    >
                      <span className="text-xs">{expandedFolders.has('__unfiled__') ? '▼' : '▶'}</span>
                      <span>📄 Unfiled</span>
                      <span className="text-xs ml-auto">{unfiledNotes.length}</span>
                    </button>
                    {expandedFolders.has('__unfiled__') && (
                      <div className="ml-5 space-y-0.5">
                        {unfiledNotes.map((n) => (
                          <NoteTreeItem
                            key={n.id}
                            note={n}
                            isSelected={selectedNote?.id === n.id}
                            onClick={() => handleSelectNote(n)}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>

        {/* ════ CENTER PANEL — Note content ══════════════════════════════ */}
        <Card className="flex-1 flex flex-col overflow-hidden p-0">
          {selectedNote ? (
            <>
              {/* Toolbar */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-txt-muted/10">
                {!isEditing ? (
                  <>
                    <h2 className="text-lg font-bold text-txt flex-1 truncate">
                      {selectedNote.title}
                    </h2>
                    <Button variant="secondary" size="sm" onClick={() => setIsEditing(true)}>
                      Edit
                    </Button>
                    <Button variant="secondary" size="sm" onClick={() => setShowMoveDialog(!showMoveDialog)}>
                      Move
                    </Button>
                    <Button variant="danger" size="sm" onClick={handleDelete}>
                      Delete
                    </Button>
                  </>
                ) : (
                  <>
                    <input
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="flex-1 bg-elevated rounded-lg px-3 py-1.5 text-lg font-bold text-txt border border-transparent focus:border-accent focus:outline-none"
                    />
                    <Button variant="primary" size="sm" onClick={handleSave}>
                      Save
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => {
                      setIsEditing(false);
                      setEditTitle(selectedNote.title);
                      setEditContent(selectedNote.content || '');
                    }}>
                      Cancel
                    </Button>
                  </>
                )}
              </div>

              {/* Move dialog */}
              {showMoveDialog && (
                <div className="px-4 py-2 bg-elevated/50 border-b border-txt-muted/10 flex flex-wrap gap-2 items-center">
                  <span className="text-txt-muted text-xs font-medium">Move to:</span>
                  <Button
                    variant={!selectedNote.folder_id ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => handleMoveNote(null)}
                  >
                    Unfiled
                  </Button>
                  {allFolders.map((f) => (
                    <Button
                      key={f.id}
                      variant={selectedNote.folder_id === f.id ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => handleMoveNote(f.id)}
                    >
                      📁 {f.name}
                    </Button>
                  ))}
                </div>
              )}

              {/* Content area */}
              <div className="flex-1 overflow-y-auto p-5">
                {isEditing ? (
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full h-full min-h-[300px] bg-elevated rounded-xl px-4 py-3 text-txt border-2 border-transparent focus:border-accent focus:outline-none transition resize-none font-mono text-sm"
                  />
                ) : (
                  <div className="prose prose-invert max-w-none">
                    <div className="text-txt whitespace-pre-wrap text-sm leading-relaxed">
                      {selectedNote.content || 'No content'}
                    </div>
                  </div>
                )}
              </div>

              {/* Bottom bar — word count + folder info */}
              <div className="px-4 py-2 border-t border-txt-muted/10 flex justify-between items-center text-xs text-txt-muted">
                <span>
                  {wordCount(selectedNote.content)} words
                  {selectedNote.folder_id && (
                    <> · 📁 {allFolders.find((f) => f.id === selectedNote.folder_id)?.name || selectedNote.folder_id}</>
                  )}
                </span>
                <span>
                  Modified: {new Date(selectedNote.last_modified).toLocaleString()}
                </span>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-3">
                <div className="text-4xl">📖</div>
                <p className="text-txt-muted">Select a note to view</p>
                <p className="text-txt-muted text-xs">or create a new one with + Note</p>
              </div>
            </div>
          )}
        </Card>

        {/* ════ RIGHT PANEL — Metadata & properties ═════════════════════ */}
        {selectedNote && (
          <Card className="w-72 flex-shrink-0 flex flex-col overflow-hidden p-0">
            <div className="px-4 py-3 border-b border-txt-muted/10">
              <h3 className="text-sm font-bold text-txt">Properties</h3>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-4">

              {/* ── Tags ──────────────────────────────────────────────── */}
              <div>
                <p className="text-xs font-bold text-txt-muted uppercase tracking-wider mb-2">Tags</p>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {(selectedNote.tags || []).length > 0 ? (
                    selectedNote.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center gap-1 bg-accent/10 text-accent rounded-full px-2.5 py-0.5 text-xs font-medium"
                      >
                        {tag}
                        <button
                          onClick={() => handleRemoveTag(tag)}
                          className="hover:text-danger transition text-[10px]"
                        >
                          ✕
                        </button>
                      </span>
                    ))
                  ) : (
                    <span className="text-txt-muted text-xs">No tags</span>
                  )}
                </div>
                <div className="flex gap-1">
                  <input
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                    placeholder="Add tag..."
                    className="flex-1 bg-elevated rounded-lg px-2 py-1 text-xs text-txt border border-transparent focus:border-accent focus:outline-none"
                  />
                  <button
                    onClick={handleAddTag}
                    disabled={!newTag.trim()}
                    className="text-accent text-xs font-bold px-2 hover:bg-accent/10 rounded-lg transition disabled:opacity-30"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* ── Folder ────────────────────────────────────────────── */}
              <div>
                <p className="text-xs font-bold text-txt-muted uppercase tracking-wider mb-1">Folder</p>
                <p className="text-sm text-txt">
                  {selectedNote.folder_id
                    ? `📁 ${allFolders.find((f) => f.id === selectedNote.folder_id)?.name || selectedNote.folder_id}`
                    : '📄 Unfiled'}
                </p>
              </div>

              {/* ── Group ─────────────────────────────────────────────── */}
              <div>
                <p className="text-xs font-bold text-txt-muted uppercase tracking-wider mb-1">Group</p>
                <input
                  value={selectedNote.group_id || ''}
                  onChange={(e) => handleSetGroup(e.target.value)}
                  placeholder="None"
                  className="w-full bg-elevated rounded-lg px-2 py-1 text-xs text-txt border border-transparent focus:border-accent focus:outline-none"
                />
              </div>

              {/* ── Permissions ────────────────────────────────────────── */}
              <div>
                <p className="text-xs font-bold text-txt-muted uppercase tracking-wider mb-1">Permissions</p>
                {Object.keys(selectedNote.permissions || {}).length > 0 ? (
                  <div className="space-y-1">
                    {Object.entries(selectedNote.permissions).map(([userId, role]) => (
                      <div key={userId} className="flex justify-between text-xs">
                        <span className="text-txt truncate">{userId}</span>
                        <Badge label={role} variant={role === 'admin' ? 'admin' : 'player'} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-txt-muted text-xs">Owner only</p>
                )}
              </div>

              {/* ── Links ─────────────────────────────────────────────── */}
              <div>
                <p className="text-xs font-bold text-txt-muted uppercase tracking-wider mb-1">
                  Links ({(selectedNote.links || []).length})
                </p>
                {(selectedNote.links || []).length > 0 ? (
                  <div className="space-y-1">
                    {selectedNote.links.map((linkId) => (
                      <button
                        key={linkId}
                        onClick={() => handleSelectNote({ id: linkId })}
                        className="block w-full text-left text-xs text-accent hover:underline truncate"
                      >
                        🔗 {linkId}
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-txt-muted text-xs">No links</p>
                )}
              </div>

              {/* ── Metadata (YAML/frontmatter) ───────────────────────── */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs font-bold text-txt-muted uppercase tracking-wider">Metadata</p>
                  <button
                    onClick={() => setShowMetaEditor(!showMetaEditor)}
                    className="text-accent text-xs font-bold hover:bg-accent/10 px-1.5 rounded transition"
                  >
                    {showMetaEditor ? '−' : '+'}
                  </button>
                </div>
                {Object.keys(selectedNote.meta || {}).length > 0 ? (
                  <div className="space-y-1">
                    {Object.entries(selectedNote.meta).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between text-xs group">
                        <span className="text-txt-muted font-medium">{k}:</span>
                        <span className="text-txt truncate ml-2">{v}</span>
                        <button
                          onClick={() => handleRemoveMeta(k)}
                          className="hidden group-hover:block text-danger text-[10px] ml-1"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-txt-muted text-xs">No metadata</p>
                )}
                {showMetaEditor && (
                  <div className="mt-2 space-y-1">
                    <input
                      value={metaKey}
                      onChange={(e) => setMetaKey(e.target.value)}
                      placeholder="Key"
                      className="w-full bg-elevated rounded-lg px-2 py-1 text-xs text-txt border border-transparent focus:border-accent focus:outline-none"
                    />
                    <input
                      value={metaValue}
                      onChange={(e) => setMetaValue(e.target.value)}
                      placeholder="Value"
                      onKeyDown={(e) => e.key === 'Enter' && handleAddMeta()}
                      className="w-full bg-elevated rounded-lg px-2 py-1 text-xs text-txt border border-transparent focus:border-accent focus:outline-none"
                    />
                    <button
                      onClick={handleAddMeta}
                      disabled={!metaKey.trim()}
                      className="text-accent text-xs font-bold hover:bg-accent/10 px-2 py-0.5 rounded transition disabled:opacity-30"
                    >
                      Add
                    </button>
                  </div>
                )}
              </div>

              {/* ── AI Summary ────────────────────────────────────────── */}
              {selectedNote.ai_summary && (
                <div>
                  <p className="text-xs font-bold text-txt-muted uppercase tracking-wider mb-1">AI Summary</p>
                  <p className="text-xs text-txt-secondary">{selectedNote.ai_summary}</p>
                </div>
              )}

              {/* ── File info ─────────────────────────────────────────── */}
              <div className="border-t border-txt-muted/10 pt-3">
                <p className="text-xs font-bold text-txt-muted uppercase tracking-wider mb-2">Info</p>
                <div className="space-y-1 text-xs text-txt-muted">
                  <div className="flex justify-between">
                    <span>Created</span>
                    <span className="text-txt">{new Date(selectedNote.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Modified</span>
                    <span className="text-txt">{new Date(selectedNote.last_modified).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Words</span>
                    <span className="text-txt">{wordCount(selectedNote.content)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Owner</span>
                    <span className="text-txt truncate ml-2">{selectedNote.owner_id || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>ID</span>
                    <span className="text-txt truncate ml-2 font-mono text-[10px]">{selectedNote.id}</span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}


// ════════════════════════════════════════════════════════════════════════════
// Sub-component: single note in tree
// ════════════════════════════════════════════════════════════════════════════

function NoteTreeItem({ note, isSelected, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-3 py-1.5 rounded-lg text-sm transition truncate ${
        isSelected
          ? 'bg-accent/10 text-accent font-medium'
          : 'text-txt hover:bg-hover'
      }`}
    >
      <div className="flex items-center gap-1.5">
        <span className="text-xs flex-shrink-0">📝</span>
        <span className="truncate">{note.title || note.name || 'Untitled'}</span>
        {(note.tags || []).length > 0 && (
          <span className="text-txt-muted text-[10px] ml-auto flex-shrink-0">
            {note.tags.length} tag{note.tags.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>
    </button>
  );
}
