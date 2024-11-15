package ChessEngine.board;

import ChessEngine.pieces.Piece;

import java.util.HashMap;
import java.util.Map;

public abstract class Tile {
    protected final int tileCoordinate;

    private static final Map<Integer, EmptyTile> EMPTY_TILES = createAllPossibleEmptyTiles();

    private static Map<Integer, EmptyTile> createAllPossibleEmptyTiles() {
        final Map<Integer, EmptyTile> emptyTileMap = new HashMap<>();

        for (int i = 0; i < 64; i++){
            emptyTileMap.put(i, new EmptyTile(i));
        }

        return emptyTileMap;
    }

    Tile(int tileCoordinate) {
        this.tileCoordinate = tileCoordinate;
    }

    public abstract boolean isTileOccupied();

    public abstract Piece getPiece();

    public static final class EmptyTile extends Tile{ //Subclass for an empty tile
        EmptyTile(final int tileCoordinate) {
            super(tileCoordinate);
        }

        @Override
        public boolean isTileOccupied() {
            return false; //tile is empty so this will be false by default
        }

        @Override
        public Piece getPiece(){
            return null; //tile is empty so this will be null by default
        }
    }

    public static final class OccupiedTile extends Tile{ //Subclass for an occupied tile
        private final Piece occupyingPiece;

        OccupiedTile(final int tileCoordinate, Piece occupyingPiece) {
            super(tileCoordinate);
            this.occupyingPiece = occupyingPiece;
        }

        @Override
        public boolean isTileOccupied() {
            return true; //tile is occupied so this will be true by default
        }

        @Override
        public Piece getPiece(){
            return this.occupyingPiece;
        }
    }
}
