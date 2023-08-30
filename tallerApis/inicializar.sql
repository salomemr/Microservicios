-- create_users_table.sql
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  hashed_password VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de prueba en la tabla users
INSERT INTO users (username, hashed_password, email) VALUES
  ('camilo23', 'contracami', 'camilo@email.com'),
  ('user1', 'contras', 'user1@email.com'),
  ('kille', 'kille12', 'kille222@email.com'),
  ('mariag21', 'mag12', 'mariag@email.com'),
  ('daniel', 'daniel11', 'daniel23@email.com');

