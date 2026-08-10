const express = require('express');
const knex = require('knex')(require('./knexfile').development);
const app = express();
require('dotenv').config();

app.use(express.json());

// Function to calculate breed based on parents
const calculateBreed = (fatherBreed, motherBreed) => {
  if (!fatherBreed || !motherBreed) return null;
  const combinations = {
    'oo_oo': 'oo',
    'oo_xo': 'xo',
    'oo_xx': 'xxoo',
    'xx_xx': 'xx',
    'xx_xo': 'xo',
    'xo_xo': 'xo',
    'xx_xxoo': 'xxoo'
  };
  return combinations[`${fatherBreed}_${motherBreed}`] || combinations[`${motherBreed}_${fatherBreed}`] || null;
};

// Validate horse data
const validateHorse = async (horse) => {
  if (!horse.name || !horse.birth_date || !horse.gender || !horse.color_id || !horse.breeder_id) {
    return 'All fields (name, birth_date, gender, color_id, breeder_id) are required';
  }
  if (!['klacz', 'ogier', 'walach'].includes(horse.gender)) {
    return 'Invalid gender';
  }
  if (horse.breed_code) {
    const breed = await knex('breeds').where({ code: horse.breed_code }).first();
    if (!breed) return 'Invalid breed_code';
  }
  const color = await knex('colors').where({ id: horse.color_id }).first();
  if (!color) return 'Invalid color_id';
  const breeder = await knex('breeders').where({ id: horse.breeder_id }).first();
  if (!breeder) return 'Invalid breeder_id';
  if (horse.father_id) {
    const father = await knex('horses').where({ id: horse.father_id }).first();
    if (!father || father.gender !== 'ogier') {
      return 'Father must be an ogier';
    }
  }
  if (horse.mother_id) {
    const mother = await knex('horses').where({ id: horse.mother_id }).first();
    if (!mother || mother.gender !== 'klacz') {
      return 'Mother must be a klacz';
    }
  }
  return null;
};

// Helper function to fetch pedigree recursively
const getPedigree = async (horseId, currentDepth) => {
  if (currentDepth <= 0) return null;

  const horse = await knex('horses')
    .select(
      'horses.id',
      'horses.name',
      'horses.birth_date',
      'horses.gender',
      'horses.breed_code',
      'horses.father_id',
      'horses.mother_id',
      'breeds.description as breed',
      'colors.name as color'
    )
    .leftJoin('breeds', 'horses.breed_code', 'breeds.code')
    .leftJoin('colors', 'horses.color_id', 'colors.id')
    .where('horses.id', horseId)
    .first();

  if (!horse) return null;

  const [father, mother] = await Promise.all([
    getPedigree(horse.father_id, currentDepth - 1),
    getPedigree(horse.mother_id, currentDepth - 1)
  ]);

  return { ...horse, father, mother };
};

// Countries Endpoints
app.get('/countries', async (req, res) => {
  try {
    const countries = await knex('countries').select('*');
    res.json(countries);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching countries' });
  }
});

app.get('/countries/:iso_code', async (req, res) => {
  try {
    const country = await knex('countries').where({ iso_code: req.params.iso_code }).first();
    if (!country) return res.status(404).json({ error: 'Country not found' });
    res.json(country);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching country' });
  }
});

app.post('/countries', async (req, res) => {
  const { iso_code, name } = req.body;
  if (!iso_code || iso_code.length !== 2 || !name) {
    return res.status(400).json({ error: 'ISO code (2 letters) and name are required' });
  }
  try {
    await knex('countries').insert({ iso_code, name }).onConflict('iso_code').ignore();
    res.status(201).json({ iso_code, name });
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error creating country' });
  }
});

app.put('/countries/:iso_code', async (req, res) => {
  const { name } = req.body;
  if (!name) return res.status(400).json({ error: 'Name is required' });
  try {
    const updated = await knex('countries').where({ iso_code: req.params.iso_code }).update({ name });
    if (!updated) return res.status(404).json({ error: 'Country not found' });
    res.json({ iso_code: req.params.iso_code, name });
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error updating country' });
  }
});

app.delete('/countries/:iso_code', async (req, res) => {
  try {
    const deleted = await knex('countries').where({ iso_code: req.params.iso_code }).del();
    if (!deleted) return res.status(404).json({ error: 'Country not found' });
    res.status(204).send();
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error deleting country' });
  }
});

// Breeders Endpoints
app.get('/breeders', async (req, res) => {
  try {
    let query = knex('breeders')
      .select('breeders.*', 'countries.name as country_name')
      .join('countries', 'breeders.country_iso_code', 'countries.iso_code');
    if (req.query.country_iso_code) {
      query = query.where('breeders.country_iso_code', req.query.country_iso_code);
    }
    const breeders = await query;
    res.json(breeders);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching breeders' });
  }
});

app.get('/breeders/:id', async (req, res) => {
  try {
    const breeder = await knex('breeders')
      .select('breeders.*', 'countries.name as country_name')
      .join('countries', 'breeders.country_iso_code', 'countries.iso_code')
      .where('breeders.id', req.params.id)
      .first();
    if (!breeder) return res.status(404).json({ error: 'Breeder not found' });
    res.json(breeder);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching breeder' });
  }
});

app.post('/breeders', async (req, res) => {
  const { name, country_iso_code } = req.body;
  if (!name || !country_iso_code) {
    return res.status(400).json({ error: 'Name and country_iso_code are required' });
  }
  const country = await knex('countries').where({ iso_code: country_iso_code }).first();
  if (!country) return res.status(400).json({ error: 'Invalid country_iso_code' });
  try {
    const [id] = await knex('breeders').insert({ name, country_iso_code }).returning('id');
    res.status(201).json({ id, name, country_iso_code });
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error creating breeder' });
  }
});

app.put('/breeders/:id', async (req, res) => {
  const { name, country_iso_code } = req.body;
  if (!name || !country_iso_code) {
    return res.status(400).json({ error: 'Name and country_iso_code are required' });
  }
  const country = await knex('countries').where({ iso_code: country_iso_code }).first();
  if (!country) return res.status(400).json({ error: 'Invalid country_iso_code' });
  try {
    const updated = await knex('breeders').where({ id: req.params.id }).update({ name, country_iso_code });
    if (!updated) return res.status(404).json({ error: 'Breeder not found' });
    res.json({ id: req.params.id, name, country_iso_code });
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error updating breeder' });
  }
});

app.delete('/breeders/:id', async (req, res) => {
  try {
    const deleted = await knex('breeders').where({ id: req.params.id }).del();
    if (!deleted) return res.status(404).json({ error: 'Breeder not found' });
    res.status(204).send();
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error deleting breeder' });
  }
});

// Colors Endpoints
app.get('/colors', async (req, res) => {
  try {
    const colors = await knex('colors').select('*');
    res.json(colors);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching colors' });
  }
});

app.get('/colors/:id', async (req, res) => {
  try {
    const color = await knex('colors').where({ id: req.params.id }).first();
    if (!color) return res.status(404).json({ error: 'Color not found' });
    res.json(color);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching color' });
  }
});

app.post('/colors', async (req, res) => {
  const { name } = req.body;
  if (!name) return res.status(400).json({ error: 'Name is required' });
  try {
    const [id] = await knex('colors').insert({ name }).returning('id');
    res.status(201).json({ id, name });
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error creating color' });
  }
});

app.put('/colors/:id', async (req, res) => {
  const { name } = req.body;
  if (!name) return res.status(400).json({ error: 'Name is required' });
  try {
    const updated = await knex('colors').where({ id: req.params.id }).update({ name });
    if (!updated) return res.status(404).json({ error: 'Color not found' });
    res.json({ id: req.params.id, name });
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error updating color' });
  }
});

app.delete('/colors/:id', async (req, res) => {
  try {
    const deleted = await knex('colors').where({ id: req.params.id }).del();
    if (!deleted) return res.status(404).json({ error: 'Color not found' });
    res.status(204).send();
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error deleting color' });
  }
});

// Breeds Endpoints
app.get('/breeds', async (req, res) => {
  try {
    const breeds = await knex('breeds').select('*');
    res.json(breeds);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching breeds' });
  }
});

app.get('/breeds/:code', async (req, res) => {
  try {
    const breed = await knex('breeds').where({ code: req.params.code }).first();
    if (!breed) return res.status(404).json({ error: 'Breed not found' });
    res.json(breed);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching breed' });
  }
});

app.post('/breeds', async (req, res) => {
  const { code, description } = req.body;
  if (!code || !description) {
    return res.status(400).json({ error: 'Code and description are required' });
  }
  try {
    await knex('breeds').insert({ code, description }).onConflict('code').ignore();
    res.status(201).json({ code, description });
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error creating breed' });
  }
});

app.put('/breeds/:code', async (req, res) => {
  const { description } = req.body;
  if (!description) return res.status(400).json({ error: 'Description is required' });
  try {
    const updated = await knex('breeds').where({ code: req.params.code }).update({ description });
    if (!updated) return res.status(404).json({ error: 'Breed not found' });
    res.json({ code: req.params.code, description });
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error updating breed' });
  }
});

app.delete('/breeds/:code', async (req, res) => {
  try {
    const deleted = await knex('breeds').where({ code: req.params.code }).del();
    if (!deleted) return res.status(404).json({ error: 'Breed not found' });
    res.status(204).send();
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error deleting breed' });
  }
});

// Horses Endpoints
app.get('/horses', async (req, res) => {
  try {
    let query = knex('horses')
      .select(
        'horses.*',
        'breeds.description as breed_description',
        'colors.name as color_name',
        'breeders.name as breeder_name'
      )
      .leftJoin('breeds', 'horses.breed_code', 'breeds.code')
      .leftJoin('colors', 'horses.color_id', 'colors.id')
      .leftJoin('breeders', 'horses.breeder_id', 'breeders.id');

    if (req.query.breed_code) query = query.where('horses.breed_code', req.query.breed_code);
    if (req.query.color_id) query = query.where('horses.color_id', req.query.color_id);
    if (req.query.breeder_id) query = query.where('horses.breeder_id', req.query.breeder_id);
    if (req.query.gender) query = query.where('horses.gender', req.query.gender);
    if (req.query.birth_date_start) query = query.where('horses.birth_date', '>=', req.query.birth_date_start);
    if (req.query.birth_date_end) query = query.where('horses.birth_date', '<=', req.query.birth_date_end);

    const horses = await query;
    res.json(horses);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching horses' });
  }
});

app.get('/horses/:id', async (req, res) => {
  try {
    const horse = await knex('horses')
      .select(
        'horses.*',
        'breeds.description as breed_description',
        'colors.name as color_name',
        'breeders.name as breeder_name'
      )
      .leftJoin('breeds', 'horses.breed_code', 'breeds.code')
      .leftJoin('colors', 'horses.color_id', 'colors.id')
      .leftJoin('breeders', 'horses.breeder_id', 'breeders.id')
      .where('horses.id', req.params.id)
      .first();
    if (!horse) return res.status(404).json({ error: 'Horse not found' });
    res.json(horse);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching horse' });
  }
});

app.post('/horses', async (req, res) => {
  const horse = req.body;
  delete horse.id; // Prevent ID override
  const validationError = await validateHorse(horse);
  if (validationError) return res.status(400).json({ error: validationError });

  try {
    if (horse.father_id && horse.mother_id && !horse.breed_code) {
      const [father, mother] = await Promise.all([
        knex('horses').where({ id: horse.father_id }).select('breed_code').first(),
        knex('horses').where({ id: horse.mother_id }).select('breed_code').first()
      ]);
      horse.breed_code = calculateBreed(father?.breed_code, mother?.breed_code) || horse.breed_code;
    }
    const [id] = await knex('horses').insert(horse).returning('id');
    const newHorse = await knex('horses').where({ id }).first();
    res.status(201).json(newHorse);
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error creating horse' });
  }
});

app.put('/horses/:id', async (req, res) => {
  const horse = req.body;
  delete horse.id; 
  const validationError = await validateHorse(horse);
  if (validationError) return res.status(400).json({ error: validationError });

  try {
    if (horse.father_id && horse.mother_id && !horse.breed_code) {
      const [father, mother] = await Promise.all([
        knex('horses').where({ id: horse.father_id }).select('breed_code').first(),
        knex('horses').where({ id: horse.mother_id }).select('breed_code').first()
      ]);
      horse.breed_code = calculateBreed(father?.breed_code, mother?.breed_code) || horse.breed_code;
    }
    const updated = await knex('horses').where({ id: req.params.id }).update(horse);
    if (!updated) return res.status(404).json({ error: 'Horse not found' });
    const updatedHorse = await knex('horses').where({ id: req.params.id }).first();
    res.json(updatedHorse);
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error updating horse' });
  }
});

app.delete('/horses/:id', async (req, res) => {
  try {
    const deleted = await knex('horses').where({ id: req.params.id }).del();
    if (!deleted) return res.status(404).json({ error: 'Horse not found' });
    res.status(204).send();
  } catch (error) {
    console.error(error);
    res.status(400).json({ error: 'Error deleting horse' });
  }
});

// wyswietlanie informacji na temat rodowodu konia o podanym id i ilosci przedstawionych generacji
app.get('/rodowod/:id/:depth', async (req, res) => {
  const horseId = parseInt(req.params.id);
  let depth = parseInt(req.params.depth) || 2;

  // Validate horse ID
  if (isNaN(horseId)) {
    return res.status(400).json({ error: 'Invalid horse ID' });
  }

  // Validate and clamp depth (1 to 5 generations)
  depth = Math.max(1, Math.min(depth, depth, 5));

  try {
    // Check if horse exists
    const horseExists = await knex('horses').where({ id: horseId }).first();
    if (!horseExists) {
      return res.status(404).json({ error: 'Horse with specified ID does not exist' });
    }

    // Fetch pedigree data using the existing getPedigree helper
    const pedigree = await getPedigree(horseId, depth);

    // Return the pedigree data in JSON format
    res.json({
      horse_id: horseId,
      depth: depth,
      pedigree: pedigree
    });
  } catch (error) {
    console.error('Error fetching pedigree data:', error.message);
    res.status(500).json({ error: 'Internal server error while fetching pedigree data' });
  }
});

// Wyswietlenie potomstwa konia o podanym id z opcjonalnym filtrem dotyczacym plci i/lub hodowcy dziecka
app.get('/potomstwo/:id', async (req, res) => {
  const horseId = parseInt(req.params.id);
  const { gender, breeder_id } = req.query;

  if (isNaN(horseId)) {
    return res.status(400).json({ error: 'Nieprawidłowe ID konia' });
  }

  try {
    const horseExists = await knex('horses').where({ id: horseId }).first();
    if (!horseExists) {
      return res.status(404).json({ error: 'Koń o podanym ID nie istnieje' });
    }

    let query = knex('horses')
      .select(
        'horses.id',
        'horses.name',
        'horses.birth_date',
        'horses.gender',
        'horses.breed_code',
        'horses.color_id',
        'horses.breeder_id',
        'horses.father_id',
        'horses.mother_id',
        'breeds.description as breed_description',
        'colors.name as color_name',
        'breeders.name as breeder_name'
      )
      .leftJoin('breeds', 'horses.breed_code', 'breeds.code')
      .leftJoin('colors', 'horses.color_id', 'colors.id')
      .leftJoin('breeders', 'horses.breeder_id', 'breeders.id')
      .where(function () {
        this.where({ father_id: horseId }).orWhere({ mother_id: horseId });
      });

    if (gender) {
      query = query.where('horses.gender', gender);
    }
    if (breeder_id) {
      query = query.where('horses.breeder_id', parseInt(breeder_id));
    }

    const offspring = await query;

    res.json({
      horse_id: horseId,
      offspring_count: offspring.length,
      offspring: offspring.map(horse => ({
        id: horse.id,
        name: horse.name,
        birth_date: horse.birth_date,
        gender: horse.gender,
        breed: {
          code: horse.breed_code,
          description: horse.breed_description || 'brak'
        },
        color: horse.color_name || 'brak',
        breeder: {
          id: horse.breeder_id,
          name: horse.breeder_name || 'brak'
        },
        father_id: horse.father_id,
        mother_id: horse.mother_id
      }))
    });
  } catch (error) {
    console.error('Błąd podczas pobierania potomstwa:', error.message);
    res.status(500).json({ error: 'Wewnętrzny błąd serwera podczas pobierania potomstwa' });
  }
});

// Endpoint dla wizualizacji rodowodu
app.get('/wizualizacja-rodowodu/:id/:depth', async (req, res) => {
  const horseId = parseInt(req.params.id);
  let depth = parseInt(req.params.depth) || 2;
  depth = Math.max(1, Math.min(depth, 5));

  if (isNaN(horseId)) {
    const errorHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Błąd</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          .error { color: red; }
        </style>
      </head>
      <body>
        <h1>Błąd</h1>
        <p class="error">Nieprawidłowe ID konia</p>
      </body>
      </html>
    `;
    return res.status(400).send(errorHtml);
  }

  const renderPedigree = (horse) => {
    if (!horse) return '';
    return `
      <li>
        <div class="node">
          ${horse.father || horse.mother ? `
            <ul>
              ${horse.father ? renderPedigree(horse.father) : '<li><div class="node empty">Brak danych o ojcu</div></li>'}
              ${horse.mother ? renderPedigree(horse.mother) : '<li><div class="node empty">Brak danych o matce</div></li>'}
            </ul>
          ` : ''}
          <strong>${horse.name}</strong> (${horse.gender})<br/>
          ID: ${horse.id}, ur.: ${new Date(horse.birth_date).toLocaleDateString('pl-PL', { day: 'numeric', month: 'long', year: 'numeric' })}<br/>
          Rasa: ${horse.breed || 'brak'} (kod: ${horse.breed_code || 'brak'}), Maść: ${horse.color || 'brak'}
        </div>
      </li>
    `;
  };

  try {
    const pedigree = await getPedigree(horseId, depth);
    if (!pedigree) {
      const errorHtml = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>Błąd</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .error { color: red; }
          </style>
        </head>
        <body>
          <h1>Błąd</h1>
          <p class="error">Koń o podanym ID nie istnieje</p>
        </body>
        </html>
      `;
      return res.status(404).send(errorHtml);
    }

    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Rodowód konia</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            padding: 20px;
          }
          .tree ul {
            padding-top: 20px;
            position: relative;
            display: flex;
            justify-content: center;
          }
          .tree ul::before {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            border-top: 1px solid #ccc;
            width: 100%;
            height: 20px;
            z-index: -1;
          }
          .tree li {
            text-align: center;
            list-style-type: none;
            position: relative;
            padding: 20px 5px 0 5px;
            flex-direction: column;
          }
          .tree li::before, .tree li::after {
            content: '';
            position: absolute;
            top: 0;
            border-top: 1px solid #ccc;
            width: 50%;
            height: 20px;
          }
          .tree li::before {
            right: 50%;
            border-right: 1px solid #ccc;
          }
          .tree li::after {
            left: 50%;
            border-left: 1px solid #ccc;
          }
          .tree li:only-child::before,
          .tree li:only-child::after {
            display: none;
          }
          .tree li:only-child {
            padding-top: 0;
          }
          .tree li:first-child::before,
          .tree li:last-child::after {
            border: 0 none;
          }
          .tree li:last-child::before {
            border-radius: 0 5px 0 0;
          }
          .tree li:first-child::after {
            border-radius: 5px 0 0 0;
          }
          .tree .node {
            border: 1px solid #ccc;
            padding: 10px;
            display: inline-block;
            border-radius: 5px;
            background: rgb(241, 241, 241);
          }
          .tree .node.empty {
            background: rgb(241, 241, 241);
            color: #999;
          }
        </style>
      </head>
      <body>
        <h1>Rodowód konia: ${pedigree.name}</h1>
        <p>Liczba generacji: ${depth}</p>
        <div class="tree">
          <ul>
            ${renderPedigree(pedigree)}
          </ul>
        </div>
      </body>
      </html>
    `;

    res.send(html);
  } catch (error) {
    console.error('Błąd podczas generowania wizualizacji rodowodu:', error.message);
    const errorHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Błąd</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          .error { color: red; }
        </style>
      </head>
      <body>
        <h1>Błąd</h1>
        <p class="error">Wewnętrzny błąd serwera podczas generowania wizualizacji rodowodu</p>
      </body>
      </html>
    `;
    res.status(500).send(errorHtml);
  }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));