package ChessEngine.board;

import ChessEngine.pieces.Piece;

public abstract class Tile {
    int tileCoordinate;

    Tile(int tileCoordinate) {
        this.tileCoordinate = tileCoordinate;
    }

    public abstract boolean isTileOccupied();

    public abstract Piece getPiece();

    public static final class EmptyTile extends Tile{ //Subclass for an empty tile
        EmptyTile(int coordinate) {
            super(coordinate);
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
        Piece occupyingPiece;

        OccupiedTile(int coordinate, Piece occupyingPiece) {
            super(coordinate);
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
