CREATE TABLE recipe (
    id int PRIMARY KEY,
    name varchar(255) NOT NULL,
    method mediumtext,
    author varchar(100),
    book varchar(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP,
    INDEX (name)
);

CREATE TABLE unit_of_measure (
    name varchar(30) PRIMARY KEY,
    name_long varchar(100),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ingredient (
    id int PRIMARY KEY,
    name varchar(255) NOT NULL,
    brand varchar(100),
    ref_unit_of_measure varchar(30) NOT NULL,
    ref_quantity decimal(6, 2) DEFAULT 1,
    ref_price decimal(6, 2) DEFAULT 0,
    available boolean DEFAULT TRUE,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP,
    INDEX (name),
    FOREIGN KEY (ref_unit_of_measure)
        REFERENCES unit_of_measure(name)
        ON UPDATE CASCADE
);

CREATE table uom_conversion (
    uom_from varchar(30) NOT NULL,
    uom_to varchar(30) NOT NULL,
    factor decimal(6, 2) NOT NULL,
    FOREIGN KEY (uom_from)
        REFERENCES unit_of_measure(name)
        ON UPDATE CASCADE,
    FOREIGN KEY (uom_to)
        REFERENCES unit_of_measure(name)
        ON UPDATE CASCADE,
    PRIMARY KEY(uom_from, uom_to)
);

CREATE TABLE recipe_ingredients (
    recipe_id int NOT NULL,
    ingredient_id int NOT NULL,
    unit_of_measure varchar(30) NOT NULL,
    ref_quantity decimal(6, 2) NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id, unit_of_measure, ref_quantity),
    FOREIGN KEY (recipe_id)
        REFERENCES recipe(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (ingredient_id)
        REFERENCES ingredient(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (unit_of_measure)
        REFERENCES unit_of_measure(name)
        ON UPDATE CASCADE
);

/* When a new unit of measure is added, create a 1:1 conversion for it */
DELIMITER $$

CREATE TRIGGER one_to_one_conversion_create
AFTER INSERT
ON unit_of_measure FOR EACH ROW
BEGIN
    INSERT INTO uom_conversion(uom_from, uom_to, factor)
    VALUES (new.name, new.name, 1)
    ;
END$$

DELIMITER ;

INSERT INTO unit_of_measure(name, name_long)
VALUES
    ("unit", "unit"),
    ("tsp", "teaspoon"),
    ("tbsp", "tablespoon"),
    ("g", "gram"),
    ("kg", "kilogram"),
    ("l", "litre"),
    ("ml", "millilitre"),
    ("handful", "handful")
;

INSERT INTO uom_conversion(uom_from, uom_to, factor)
VALUES
    ("l", "ml", 1000),
    ("ml", "l", 0.001),
    ("kg", "g", 1000),
    ("g", "kg", 0.001)
;
